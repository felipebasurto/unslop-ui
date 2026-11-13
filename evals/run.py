#!/usr/bin/env python3
"""Run /unslop-ui on the fixtures and check what it did.

The counter rewards deleting. These fixtures check the other half: what has
to survive (real state, accessible names, a clean screen, text owned by a
translation file) and what must not be invented.

Usage:
  python3 evals/run.py                     run the agent on every fixture, then check
  python3 evals/run.py form claims         only these fixtures
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
FIXTURES = os.path.join(HERE, "fixtures")
EXPECT = os.path.join(HERE, "expect.json")
DEFAULT_AGENT = "claude -p --permission-mode acceptEdits"
DEFAULT_PROMPT = "/unslop-ui ."
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


def run_agent(agent, prompt, name, workdir):
    """Copy the fixture, run the agent in the copy, save its report next to it."""
    target = os.path.join(workdir, name)
    shutil.copytree(os.path.join(FIXTURES, name), target)
    try:
        result = subprocess.run(
            shlex.split(agent) + [prompt], cwd=target, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
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
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="how this agent invokes the skill (default: %(default)s)")
    parser.add_argument("--check", metavar="DIR", help="skip the agent and check edited copies in DIR/<fixture>/")
    args = parser.parse_args()

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
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as pool:
            exit_codes = dict(zip(names, pool.map(lambda n: run_agent(args.agent, args.prompt, n, workdir), names)))

    failed_any = False
    for name in names:
        failed = check_fixture(name, os.path.join(workdir, name), expectations)
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
