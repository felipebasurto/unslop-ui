#!/usr/bin/env python3
"""Run /unslop-ui on the fixtures and check what it did.

The counter rewards deleting. These fixtures check the other half: what has
to survive (real state, accessible names, a clean screen, text owned by a
translation file) and what must not be invented.

Usage:
  python3 evals/run.py                     run the agent on every fixture, then check
  python3 evals/run.py form claims         only these fixtures
  python3 evals/run.py --check DIR         check copies an agent already edited
  python3 evals/run.py --incidents         replay evals/incidents/*.json against the counter and the rules; no agent
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
COUNTER = os.path.join(ROOT, "skills", "unslop-ui", "scripts", "count_tells.py")
INCIDENTS = os.path.join(HERE, "incidents")
FIXTURES = os.path.join(HERE, "fixtures")
EXPECT = os.path.join(HERE, "expect.json")
DEFAULT_AGENT = "claude -p --permission-mode acceptEdits"
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


def load_incidents():
    """Every incident in evals/incidents, sorted by id."""
    incidents = []
    for name in sorted(os.listdir(INCIDENTS)):
        if name.endswith(".json"):
            with open(os.path.join(INCIDENTS, name), encoding="utf-8") as f:
                incidents.append(json.load(f))
    return incidents


def counter_output(case):
    """Counts the counter gives for an incident's source, run from a folder of its own."""
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, "sample" + case["suffix"]), "w", encoding="utf-8") as f:
            f.write(case["source"])
        if "taste" in case:
            os.mkdir(os.path.join(folder, ".unslop-ui"))
            with open(os.path.join(folder, ".unslop-ui", "taste.md"), "w", encoding="utf-8") as f:
                f.write(case["taste"])
        result = subprocess.run(
            [sys.executable, COUNTER] + case.get("flags", []) + ["sample" + case["suffix"]],
            cwd=folder, capture_output=True, text=True,
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return {rule: entry["count"] for rule, entry in json.loads(result.stdout).items() if rule != "total"}


def check_incident(incident):
    """Failures for one incident: its rule phrase must be written down, and the counter must keep behaving."""
    failures = []
    rule = incident["rule"]
    if rule["phrase"] not in read(os.path.join(ROOT, rule["file"])):
        failures.append("{} no longer says {!r}".format(rule["file"], rule["phrase"]))
    case = incident.get("counter")
    if case:
        counts = counter_output(case)
        failures += ["{}: not a rule this run counts (typo, or a flag or taste ban is missing)".format(name) for name in sorted(case["expect"]) if name not in counts]
        for name in sorted(counts):
            want, got = case["expect"].get(name, 0), counts[name]
            if want != got:
                failures.append("{}: expected {}, counted {}".format(name, want, got))
    return failures


def install_skill(target, dest):
    """Copy the working tree's skill into a fixture copy, renamed so it cannot clash with an installed one."""
    skill = os.path.join(target, dest)
    shutil.copytree(SKILL_SOURCE, skill, ignore=shutil.ignore_patterns("__pycache__"))
    path = os.path.join(skill, "SKILL.md")
    text = read(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace("name: unslop-ui\n", "name: {}\n".format(EVAL_SKILL), 1))


def run_agent(agent, prompt, name, workdir, skill_dest=None, extra_args=""):
    """Copy the fixture, run the agent in the copy, save its report next to it."""
    target = os.path.join(workdir, name)
    shutil.copytree(os.path.join(FIXTURES, name), target)
    if skill_dest:
        install_skill(target, skill_dest)
    try:
        result = subprocess.run(
            shlex.split(agent) + [(prompt + " " + extra_args).strip()], cwd=target, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
        report, code = result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        report, code = "Timed out after {}s".format(TIMEOUT_SECONDS), 1
    except OSError as e:
        report, code = "Could not start the agent: {}".format(e), 1
    with open(os.path.join(workdir, name + ".report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    return code


def main():
    parser = argparse.ArgumentParser(description="Run /unslop-ui on the fixtures and check the result.")
    parser.add_argument("fixtures", nargs="*", help="fixture names (default: all)")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help="agent command; the prompt is appended (default: %(default)s)")
    parser.add_argument("--prompt", help="how this agent invokes the skill (default: {}, or /unslop-ui . with --no-install-skill)".format(DEFAULT_PROMPT))
    parser.add_argument("--check", metavar="DIR", help="skip the agent and check edited copies in DIR/<fixture>/")
    parser.add_argument("--skill-dest", default=DEFAULT_SKILL_DEST, help="where in each fixture copy to install this checkout's skill (default: %(default)s)")
    parser.add_argument("--no-install-skill", action="store_true", help="do not copy the skill; the agent uses what is installed")
    parser.add_argument("--incidents", action="store_true", help="replay the incident files; needs no agent")
    args = parser.parse_args()

    if args.incidents:
        failed_any = False
        for incident in load_incidents():
            failures = check_incident(incident)
            failed_any = failed_any or bool(failures)
            print("{}  {}".format("FAIL" if failures else "ok  ", incident["id"]))
            for failure in failures:
                print("      " + failure)
        sys.exit(1 if failed_any else 0)

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
                lambda n: run_agent(args.agent, prompt, n, workdir, dest, expectations[n].get("args", "")), names)))

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
