#!/usr/bin/env python3
"""Opt-in edit hook for Claude Code and Cursor.

Runs after the agent writes a file, counts the tells in that one file with
count_tells.py and hands the agent a short note when it finds any. It never
edits anything, never blocks, and fails open: any problem exits 0 in silence.

Claude Code: PostToolUse, matcher "Edit|Write|MultiEdit".
Cursor: postToolUse, matcher "Write".
Set UNSLOP_UI_SURFACE=1 to count the --surface rules too. A taste file in the
project (.unslop-ui/taste.md) is honored, Off rules included.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import count_tells  # noqa: E402


def project_root(payload):
    roots = payload.get("workspace_roots") or []
    return payload.get("cwd") or (roots[0] if roots else os.getcwd())


def note(path, root, results):
    parts = []
    for rule, entry in results.items():
        if rule == "total" or not entry["count"]:
            continue
        lines = sorted({example.rpartition(":")[2] for example in entry["examples"]}, key=int)
        parts.append("{} x{} (line {})".format(rule, entry["count"], ", ".join(lines)))
    shown = os.path.relpath(path, root)
    return (
        "unslop-ui found {} possible AI tell{} in {}: {}. Read them: cut the ones that are tells, keep the ones tied to "
        "real state and say which you kept. For the full pass run /unslop-ui {}."
    ).format(results["total"], "" if results["total"] == 1 else "s", shown, "; ".join(parts), shown)


def respond(payload, text):
    if "cursor_version" in payload:
        return {"additional_context": text}
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}


def main():
    try:
        payload = json.load(sys.stdin)
        path = (payload.get("tool_input") or {}).get("file_path")
        if not path or not os.path.isfile(path):
            return 0
        if os.path.splitext(path)[1].lower() not in count_tells.KIND_OF:
            return 0
        if set(os.path.normpath(path).split(os.sep)) & count_tells.SKIP_DIRS:
            return 0
        root = project_root(payload)
        os.chdir(root)
        bans, off = count_tells.read_taste(count_tells.TASTE_FILE)
        results = count_tells.count([path], os.environ.get("UNSLOP_UI_SURFACE") == "1", bans, off)
        if results["total"]:
            print(json.dumps(respond(payload, note(path, root, results))))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
