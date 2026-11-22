#!/usr/bin/env python3
"""Run /unslop-ui on the fixtures and check what it did.

Each fixture is a small screen plus what must be true after a run: what has
to go, what has to survive (real state, accessible names, a clean screen,
text owned by a translation file) and what must not be invented.

Usage:
  python3 evals/run.py                     run the agent on every fixture, then check
  python3 evals/run.py form claims         only these fixtures
  python3 evals/run.py --triggers          check whether the description triggers on evals/triggers.json
  python3 evals/run.py --check DIR         check copies an agent already edited
  python3 evals/run.py --agent 'codex exec' --prompt '$unslop-ui .'   another agent

Exits 1 when a check fails.
"""
import argparse
import concurrent.futures
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIXTURES = os.path.join(HERE, "fixtures")
EXPECT = os.path.join(HERE, "expect.json")
TRIGGERS = os.path.join(HERE, "triggers.json")
DEFAULT_AGENT = "claude -p --permission-mode acceptEdits"
DEFAULT_TRIGGER_AGENT = "claude -p --setting-sources project --output-format stream-json --verbose --permission-mode plan --disallowedTools Write Edit Bash WebFetch WebSearch"
# The working tree's skill is copied into each fixture under this name, so the
# run tests the code in this checkout and not a copy installed on the machine.
EVAL_SKILL = "unslop-ui-eval"
SKILL_SOURCE = os.path.join(ROOT, "skills", "unslop-ui")
DEFAULT_SKILL_DEST = os.path.join(".claude", "skills", EVAL_SKILL)
DEFAULT_PROMPT = "/" + EVAL_SKILL + " ."
MAX_PARALLEL = 4
TIMEOUT_SECONDS = 900
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def load_expectations():
    with open(EXPECT, encoding="utf-8") as f:
        return json.load(f)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_file(before, after, spec):
    """Failures for one file, as short strings."""
    if spec.get("unchanged"):
        return [] if before == after else ["changed, expected no edit"]
    failures = []
    failures += ["lost {!r}".format(s) for s in spec.get("keep", []) if s not in after]
    failures += ["lost /{}/".format(p) for p in spec.get("keep_regex", []) if not re.search(p, after)]
    failures += ["still has {!r}".format(s) for s in spec.get("cut", []) if s in after]
    failures += ["still has /{}/".format(p) for p in spec.get("cut_regex", []) if re.search(p, after)]
    if spec.get("no_new_numbers"):
        invented = sorted(set(NUMBER.findall(after)) - set(NUMBER.findall(before)))
        if invented:
            failures.append("new numbers {}".format(", ".join(invented)))
    if spec.get("valid_json"):
        try:
            json.loads(after)
        except ValueError as e:
            failures.append("invalid JSON: {}".format(e))
    return failures


def check_report(name, workdir, expectations):
    """Failures for what the agent said, from the run's saved report."""
    patterns = expectations[name].get("report_regex", [])
    if not patterns:
        return []
    path = os.path.join(workdir, name + ".report.md")
    if not os.path.exists(path):
        return ["no report to check"]
    report = read(path)
    return ["report lacks /{}/".format(p) for p in patterns if not re.search(p, report)]


def check_fixture(name, after_dir, expectations):
    """Failures for one fixture: {file: [failure, ...]} with only failing files."""
    failed = {}
    for filename, spec in expectations[name]["files"].items():
        after_path = os.path.join(after_dir, filename)
        if not os.path.exists(after_path):
            failed[filename] = ["file deleted"]
            continue
        failures = check_file(read(os.path.join(FIXTURES, name, filename)), read(after_path), spec)
        if failures:
            failed[filename] = failures
    return failed


def install_skill(target, dest, source=SKILL_SOURCE):
    """Copy a skill (the working tree's by default) into a fixture copy, renamed so it cannot clash with an installed one."""
    skill = os.path.join(target, dest)
    shutil.copytree(source, skill, ignore=shutil.ignore_patterns("__pycache__"))
    path = os.path.join(skill, "SKILL.md")
    text = read(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace("name: unslop-ui\n", "name: {}\n".format(EVAL_SKILL), 1))


def run_agent(agent, prompt, name, workdir, skill_dest=None, extra_args="", skill_source=SKILL_SOURCE):
    """Copy the fixture, run the agent in the copy, save its report next to it."""
    target = os.path.join(workdir, name)
    shutil.copytree(os.path.join(FIXTURES, name), target)
    if skill_dest:
        install_skill(target, skill_dest, skill_source)
    try:
        result = subprocess.run(
            shlex.split(agent) + [(prompt + " " + extra_args).strip()],
            cwd=target, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
        report, code = result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        report, code = "Timed out after {}s".format(TIMEOUT_SECONDS), 1
    except OSError as e:
        report, code = "Could not start the agent: {}".format(e), 1
    with open(os.path.join(workdir, name + ".report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    return code


def run_trigger_case(agent, case, workdir, skill_dest, skill_source):
    """Run one trigger query in an isolated project with only this checkout's skill installed."""
    target = os.path.join(workdir, case["id"])
    os.makedirs(target, exist_ok=True)
    for relpath, content in case.get("files", {}).items():
        fpath = os.path.abspath(os.path.join(target, relpath))
        if not fpath.startswith(os.path.abspath(target) + os.sep):
            raise ValueError("trigger file escapes temp dir: {!r}".format(relpath))
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
    install_skill(target, skill_dest, skill_source)
    # Keep the canonical skill name inside the isolated project so trigger matching tests the real name.
    skill_md = os.path.join(target, skill_dest, "SKILL.md")
    with open(skill_md, "w", encoding="utf-8") as f:
        f.write(read(skill_md).replace("name: {}\n".format(EVAL_SKILL), "name: unslop-ui\n", 1))
    try:
        result = subprocess.run(
            shlex.split(agent) + ["--", case["query"]],
            cwd=target, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=180,
        )
        raw, code = result.stdout + "\n" + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        raw, code = "Timed out", 1
    except OSError as e:
        raw, code = "Could not start the agent: {}".format(e), 1
    with open(os.path.join(workdir, case["id"] + ".stream.jsonl"), "w", encoding="utf-8") as f:
        f.write(raw)
    triggered = False
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        msg = event.get("message") or {}
        for block in msg.get("content", []) if isinstance(msg, dict) else []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            tool = block.get("name", "")
            inp = block.get("input") or {}
            if tool == "Skill" and "unslop-ui" in str(inp.get("skill", "")):
                triggered = True
            elif tool == "Read" and "SKILL.md" in str(inp.get("file_path", "")):
                triggered = True
    return triggered, code


def run_triggers(args):
    with open(TRIGGERS, encoding="utf-8") as f:
        cases = json.load(f)
    if args.fixtures:
        wanted = set(args.fixtures)
        unknown = sorted(wanted - {c["id"] for c in cases})
        if unknown:
            sys.exit("unknown trigger id: {}".format(", ".join(unknown)))
        cases = [c for c in cases if c["id"] in wanted]
    agent = args.trigger_agent
    dest = os.path.join(".claude", "skills", "unslop-ui")
    workdir = tempfile.mkdtemp(prefix="unslop-ui-triggers-")
    print("Running {} trigger cases in {}".format(len(cases), workdir), file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(cases), MAX_PARALLEL)) as pool:
        results = list(pool.map(lambda c: run_trigger_case(agent, c, workdir, dest, args.skill_source), cases))
    failed = 0
    for case, (triggered, code) in zip(cases, results):
        expected = case["should_trigger"]
        ok = (triggered == expected) and (code == 0)
        if not ok:
            failed += 1
        tag = "ok  " if ok else "FAIL"
        want = "trigger" if expected else "skip"
        got = "triggered" if triggered else "skipped"
        extra = "" if code == 0 else " (exit {})".format(code)
        print("{}  {:<26} expected={:<7} got={}{}".format(tag, case["id"], want, got, extra))
    print("\nPassed {}/{}. Logs: {}".format(len(cases) - failed, len(cases), workdir))
    sys.exit(1 if failed else 0)


def main():
    parser = argparse.ArgumentParser(description="Run /unslop-ui on the fixtures and check the result.")
    parser.add_argument("fixtures", nargs="*", help="fixture or trigger names (default: all)")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help="agent command; the prompt is appended (default: %(default)s)")
    parser.add_argument("--triggers", action="store_true", help="evaluate description triggering against evals/triggers.json")
    parser.add_argument("--trigger-agent", default=DEFAULT_TRIGGER_AGENT, help="agent command for --triggers (default: %(default)s)")
    parser.add_argument("--prompt", help="how this agent invokes the skill (default: {}, or /unslop-ui . with --no-install-skill)".format(DEFAULT_PROMPT))
    parser.add_argument("--check", metavar="DIR", help="skip the agent and check edited copies in DIR/<fixture>/")
    parser.add_argument("--skill-dest", default=DEFAULT_SKILL_DEST, help="where in each fixture copy to install this checkout's skill (default: %(default)s)")
    parser.add_argument("--skill-source", default=SKILL_SOURCE, help="skill folder to install, to compare another version (default: this checkout's)")
    parser.add_argument("--no-install-skill", action="store_true", help="do not copy the skill; the agent uses what is installed")
    args = parser.parse_args()

    if args.triggers:
        run_triggers(args)

    expectations = load_expectations()
    names = args.fixtures or sorted(expectations)
    unknown = [n for n in names if n not in expectations]
    if unknown:
        parser.error("unknown fixture: {} (have: {})".format(", ".join(unknown), ", ".join(sorted(expectations))))

    workdir = args.check
    exit_codes = {}
    if not workdir:
        workdir = tempfile.mkdtemp(prefix="unslop-ui-eval-")
        print("Running {!r} on {} fixtures in {}".format(args.agent, len(names), workdir), file=sys.stderr)
        dest = None if args.no_install_skill else args.skill_dest
        prompt = args.prompt or ("/unslop-ui ." if args.no_install_skill else DEFAULT_PROMPT)
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(names), MAX_PARALLEL)) as pool:
            exit_codes = dict(zip(names, pool.map(
                lambda n: run_agent(args.agent, prompt, n, workdir, dest, expectations[n].get("args", ""), args.skill_source), names)))

    failed_any = False
    for name in names:
        failed = check_fixture(name, os.path.join(workdir, name), expectations)
        reported = check_report(name, workdir, expectations)
        if reported:
            failed["report"] = reported
        if exit_codes.get(name):
            failed["agent"] = ["exit code {}, see {}.report.md".format(exit_codes[name], name)]
        failed_any = failed_any or bool(failed)
        print("{}  {}".format("FAIL" if failed else "ok  ", name))
        for filename, failures in failed.items():
            for failure in failures:
                print("      {}: {}".format(filename, failure))
    print("\nEdited copies and reports: {}".format(workdir))
    sys.exit(1 if failed_any else 0)


if __name__ == "__main__":
    main()
