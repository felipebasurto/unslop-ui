#!/usr/bin/env python3
"""Count UI slop candidates in a file or folder.

Usage: python3 count_tells.py <file-or-folder> [...]

Prints JSON: {rule: {"count": n, "examples": ["file:line", ...]}}.
Regex heuristic for before/after comparison. It misses tells that need
reading (U3, U4, U5, U7, U8, U12, U13) and can flag legitimate cases.
"""
import json
import os
import re
import sys

EXTENSIONS = {".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro", ".md", ".mdx"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".svelte-kit", ".astro", "coverage"}
# Enough to show where to look without flooding the agent's context.
MAX_EXAMPLES = 5

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U00002B50\U00002B55\U0000231A-\U0000231B\U000023E9-\U000023FA]"
)

RULES = [
    ("U1 eyebrow", re.compile(r"\buppercase\b.*\b(tracking-|letter-spacing)|\b(tracking-|letter-spacing).*\buppercase\b|text-transform:\s*uppercase")),
    ("U2 decorative numbering", re.compile(r">\s*0[1-9](?:\s|<|\.|/)|['\"`]0[1-9]['\"`]|>[^<>{}]*?(?<!:)//[^<>]*<")),
    ("U6 status string", re.compile(r"·|&middot;|&#183;|\\u00b7")),
    ("U9 badge word", re.compile(r">\s*(?:LIVE|Live|NEW|New|BETA|Beta|AI|PRO|Pro|HOT|Hot)\s*<|['\"`](?:LIVE|NEW|BETA|HOT)['\"`]")),
    ("U10 status dot", re.compile(r"animate-pulse|animate-ping|\brounded-full\b(?=.*\b(?:size-[12](?:\.5)?|[hw]-(?:1|1\.5|2|2\.5))\b)")),
    ("U11 emoji", EMOJI),
    ("unslop 13 em dash", re.compile(r"—|&mdash;|&#8212;|\\u2014")),
]


def iter_files(targets):
    for target in targets:
        if os.path.isfile(target):
            yield target
            continue
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if os.path.splitext(name)[1].lower() in EXTENSIONS:
                    yield os.path.join(root, name)


def is_code_comment(line):
    stripped = line.lstrip()
    return stripped.startswith(("//", "/*", "*", "#"))


def main():
    targets = sys.argv[1:]
    if not targets:
        print("Usage: python3 count_tells.py <file-or-folder> [...]", file=sys.stderr)
        sys.exit(2)
    missing = [t for t in targets if not os.path.exists(t)]
    if missing:
        print("Not found: " + ", ".join(missing), file=sys.stderr)
        sys.exit(2)

    results = {name: {"count": 0, "examples": []} for name, _ in RULES}
    for path in iter_files(targets):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            print("Skipped {}: {}".format(path, e), file=sys.stderr)
            continue
        for lineno, line in enumerate(lines, 1):
            if is_code_comment(line):
                continue
            for name, regex in RULES:
                hits = len(regex.findall(line))
                if hits:
                    entry = results[name]
                    entry["count"] += hits
                    if len(entry["examples"]) < MAX_EXAMPLES:
                        entry["examples"].append("{}:{}".format(path, lineno))

    results["total"] = sum(r["count"] for r in results.values())
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
