#!/usr/bin/env python3
"""Print the pattern list of the newest installed /pstack:unslop skill.

Called through dynamic context injection when /unslop-ui is invoked, so it
must always exit 0: a non-zero exit would abort the whole skill.
"""
import glob
import os
import re

# Where Claude Code, Cursor, Codex and `npx skills` put plugin and skill folders.
SEARCH = [
    "~/.claude/plugins/cache/*/pstack/*/skills/unslop/SKILL.md",
    "~/.cursor/plugins/**/pstack/**/skills/unslop/SKILL.md",
    "~/.claude/skills/unslop/SKILL.md",
    "~/.cursor/skills/unslop/SKILL.md",
    "~/.agents/skills/unslop/SKILL.md",
    "~/.codex/skills/unslop/SKILL.md",
    ".claude/skills/unslop/SKILL.md",
    ".cursor/skills/unslop/SKILL.md",
    ".agents/skills/unslop/SKILL.md",
]

FALLBACK = (
    "/pstack:unslop is not installed (https://github.com/cursor/plugins/tree/main/pstack). "
    "Apply at least: no AI vocabulary (delve, seamless, crucial, enhance, showcase), "
    "no em dashes, sentence-case headings, no decorative emojis, say what it does "
    "instead of how it feels, prefer the plain word."
)


def version_key(path):
    # Compare paths by their numeric parts so 0.15.20 sorts after 0.15.9.
    return [int(p) for p in re.findall(r"\d+", path)]


def find_unslop():
    for pattern in SEARCH:
        paths = glob.glob(os.path.expanduser(pattern), recursive=True)
        if paths:
            return max(paths, key=version_key)
    return None


def main():
    path = find_unslop()
    if not path:
        print(FALLBACK)
        return
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        print(FALLBACK)
        return
    # Drop the frontmatter and the skill's own intro; keep the numbered rules.
    start = text.find("## Patterns to detect and fix")
    print(text[start:] if start != -1 else re.sub(r"\A---.*?---\s*", "", text, flags=re.S))


if __name__ == "__main__":
    main()
