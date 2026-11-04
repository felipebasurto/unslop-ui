#!/usr/bin/env python3
"""Count UI slop candidates in a file or folder.

Usage: python3 count_tells.py [--surface] <file-or-folder> [...]

Prints JSON: {rule: {"count": n, "examples": ["file:line", ...]}}.
Regex heuristic for before/after comparison. It misses tells that need
reading (U3, U4, U5, U7, U8, U12, U13, U14) and can flag legitimate cases.
--surface adds the visual rules U17 to U20 (gradients and glows, off-scale
spacing, extra-heavy weights, motion).
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
    ("U15 chart scaffolding", re.compile(r"feDropShadow|drop-shadow\(|shadowBlur|shadowColor|\bminor\s*:\s*\{|border\s*:\s*\{[^}]*width\s*:\s*(?:[2-9]|1\.[5-9])|grid\s*:\s*\{[^}]*lineWidth\s*:\s*(?:[2-9]|1\.[5-9])")),
    ("U16 legend", re.compile(r"legend\s*:\s*\{[^}]*display\s*:\s*true|<Legend\b")),
    ("unslop 13 em dash", re.compile(r"—|&mdash;|&#8212;|\\u2014")),
]


SPACING_UTILITY = re.compile(r"(?<![\w-])-?(?:[mp][trblxyse]?|gap(?:-[xy])?|space-[xy])-\[(\d+)px\]")
SPACING_PROPERTY = re.compile(r"\b(?:margin|padding)(?:-(?:top|right|bottom|left))?\s*:\s*(\d+)px\s*(?:[;}\"']|$)|\bgap\s*:\s*(\d+)px")


def count_off_scale(line):
    values = [m.group(1) for m in SPACING_UTILITY.finditer(line)]
    for m in SPACING_PROPERTY.finditer(line):
        values.append(m.group(1) or m.group(2))
    return sum(1 for v in values if int(v) % 4 != 0 and int(v) != 2)


def regex_counter(regex):
    return lambda line: len(regex.findall(line))


RULES = [(name, regex_counter(regex)) for name, regex in RULES]

SURFACE_RULES = [
    ("U17 gradient or glow", regex_counter(re.compile(
        r"\bbg-(?:gradient|linear|radial|conic)-to?-?|(?:linear|radial|conic)-gradient\(|\bbg-clip-text\b|background-clip:\s*text"
        r"|\bblur-(?:2xl|3xl)\b|\bshadow-\[0_0_|\bshadow-[a-z]+-\d{2,3}(?:/\d+)?\b|box-shadow:[^;]*\b0\s+0\s+\d+px"
    ))),
    ("U18 off-scale spacing", count_off_scale),
    ("U19 extra-heavy weight", regex_counter(re.compile(
        r"\bfont-(?:extrabold|black)\b|font-?[wW]eight\W{0,3}[89]00\b|\bfont-\[[89]00\]"
    ))),
    ("U20 motion", regex_counter(re.compile(
        r"\btransition-all\b|transition:\s*all\b|\bhover:scale-|\banimate-bounce\b"
    ))),
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
    args = sys.argv[1:]
    surface = "--surface" in args
    targets = [a for a in args if a != "--surface"]
    if not targets:
        print("Usage: python3 count_tells.py [--surface] <file-or-folder> [...]", file=sys.stderr)
        sys.exit(2)
    missing = [t for t in targets if not os.path.exists(t)]
    if missing:
        print("Not found: " + ", ".join(missing), file=sys.stderr)
        sys.exit(2)

    rules = RULES + SURFACE_RULES if surface else RULES
    results = {name: {"count": 0, "examples": []} for name, _ in rules}
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
            for name, counter in rules:
                hits = counter(line)
                if hits:
                    entry = results[name]
                    entry["count"] += hits
                    if len(entry["examples"]) < MAX_EXAMPLES:
                        entry["examples"].append("{}:{}".format(path, lineno))

    results["total"] = sum(r["count"] for r in results.values())
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
