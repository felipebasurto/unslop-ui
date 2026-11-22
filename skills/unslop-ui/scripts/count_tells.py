#!/usr/bin/env python3
"""Count UI slop candidates in a file or folder.

Usage: python3 count_tells.py [--surface] [--max N] [--taste PATH] [--format json|github] <file-or-folder> [...]

Prints JSON: {rule: {"count": n, "examples": ["file:line", ...]}, "total": n}.
Regex heuristic for before/after comparison. It never reads words, so it works
the same on copy in any language: it counts structure (classes, markup, glyphs,
chart config). Everything that depends on what a string means (U3, U4, U5, U7,
U8, U12, U13, U14, U22, U24, U25, filler words, generic names) is left to the
agent, which reads the copy in whatever language it is written. The counter can
flag legitimate cases too.
--surface adds the visual rules U17 to U20 and U26 (gradients and glows,
off-scale spacing, extra-heavy weights, motion, edge accent bars).
--max N exits 1 when the total is above N, for CI.
A taste file (.unslop-ui/taste.md in the current folder, or --taste PATH)
turns on T1 to T3 for the bans it lists (exclamation marks, uppercase text,
middle dots) and switches off every rule its Off section lists.
--format github prints workflow annotations instead of JSON, for CI.
"""
import argparse
import bisect
import json
import os
import re
import sys

KINDS = {
    "markup": {".html", ".htm", ".jsx", ".tsx", ".js", ".mjs", ".cjs", ".ts", ".vue", ".svelte", ".astro"},
    "prose": {".md", ".mdx"},
    "style": {".css", ".scss", ".less"},
    "data": {".json"},
    "python": {".py"},
}
KIND_OF = {ext: kind for kind, exts in KINDS.items() for ext in exts}
SKIP_DIRS = {"node_modules", ".git", ".unslop-ui", ".claude", ".cursor", ".agents", ".codex", ".devin", ".windsurf", "dist", "build", ".next", ".svelte-kit", ".astro", "coverage", ".venv", "venv", "__pycache__"}
SKIP_FILES = {"package-lock.json", "package.json"}
# Minified bundles and data dumps are not hand-written interface code.
MAX_BYTES = 1_000_000
# Enough to show where to look without flooding the agent's context.
MAX_EXAMPLES = 5

ALL = set(KINDS)
TEXT = ALL - {"style"}


def blank(match):
    return re.sub(r"[^\n]", " ", match.group(0))


COMMENTS = {
    "block": re.compile(r"^[ \t]*/\*.*?\*/", re.S | re.M),
    "jsx": re.compile(r"\{/\*.*?\*/\}", re.S),
    "html": re.compile(r"<!--.*?-->", re.S),
    "line": re.compile(r"^[ \t]*//.*$", re.M),
    # After code punctuation only, so "https://" and a "01 // Features" text node survive.
    "trailing": re.compile(r"(?<=[;,{}()\[\]])[ \t]*//(?!/)[^<\n]*$", re.M),
    "hash": re.compile(r"^[ \t]*#.*$", re.M),
}
COMMENTS_FOR = {
    "markup": ("jsx", "html", "block", "line", "trailing"),
    "prose": ("jsx", "html"),
    "style": ("block", "line"),
    "data": (),
    "python": ("hash",),
}


def strip_comments(text, kind):
    """Blank comments out, keeping every offset and line number."""
    for name in COMMENTS_FOR[kind]:
        text = COMMENTS[name].sub(blank, text)
    return text


def rx(pattern, flags=0):
    regex = re.compile(pattern, flags)
    return lambda text: [m.start() for m in regex.finditer(text)]


def enclosing_tag(text, pos):
    """Name of the tag opened last before pos, or ''."""
    start = text.rfind("<", max(0, pos - 400), pos + 1)
    match = re.match(r"</?([A-Za-z][\w.-]*)", text[start:start + 60]) if start != -1 else None
    return match.group(1) if match else ""


def quoted_segment(text, pos):
    """The string literal around pos, or its line when there are no quotes."""
    lo = max(0, pos - 400)
    before = max(text.rfind(q, lo, pos) for q in "\"'`")
    after = [i for i in (text.find(q, pos, pos + 400) for q in "\"'`") if i != -1]
    if before == -1 or not after:
        return text.rfind("\n", 0, pos) + 1, (text.find("\n", pos) + 1 or len(text))
    return before + 1, min(after)


# U1: uppercase plus widened tracking in one class string. Table headers and
# key caps use the same styling and are not eyebrows.
EYEBROW = re.compile(
    r"\buppercase\b[^\"'`<>]{0,200}?\btracking-(?!tight|normal)"
    r"|\btracking-(?!tight|normal)[^\"'`<>]{0,200}?\buppercase\b"
    r"|text-transform:\s*uppercase|textTransform:\s*[\"']uppercase"
)
NOT_EYEBROW_TAGS = {"th", "TableHead", "TableHeader", "kbd", "abbr"}


def eyebrows(text):
    return [m.start() for m in EYEBROW.finditer(text) if enclosing_tag(text, m.start()) not in NOT_EYEBROW_TAGS]


# U2: "01", "01.", "01 //" as text, a zero-padded index, or "//" used as an
# ornament inside a text node. Dates and times ("01/02", "01:30") are not it.
NUMBERING = (
    r">\s*0[1-9](?![/:.\-]\d)(?:\s|<|\.|/)"
    r"|(?<![=\w])['\"`]0[1-9]['\"`]"
    r"|>[^<>{}\n]*?(?<!:)//[^<>\n]*<"
    r"|padStart\(\s*2\s*,\s*['\"`]0['\"`]\s*\)"
    r"|>\s*0\{"
)
ORDERED_LIST = re.compile(r"<(ol)(?![\w.-])")


def numbering(text):
    """U2 hits outside an ordered list: inside an <ol> the order is real."""
    return [p for p in rx(NUMBERING)(text) if open_element_before(text, p, ORDERED_LIST) is None]


# In prose a backticked "01" is a code reference, not a label.
NUMBERING_PROSE = (
    r">\s*0[1-9](?![/:.\-]\d)(?:\s|<|\.|/)"
    r"|>[^<>{}\n]*?(?<!:)//[^<>\n]*<"
    r"|>\s*0\{"
)
# U6: two or more separators close together make a chain. One separator
# ("Jan 3 · 14:02") is ordinary punctuation.
SEPARATOR = re.compile(r"·|•|&middot;|&#183;|&bull;|\\u00b7|\\u2022")
JOINED = re.compile(r"join\(\s*['\"`]\s*(?:·|•|\|)\s*['\"`]\s*\)")
PIPED = re.compile(r">[^<>{}\n]*\s\|\s[^<>{}\n]*\s\|\s[^<>{}\n]*<")
CHAIN_GAP = 200


def separator_clusters(text):
    """Runs of separators less than CHAIN_GAP apart, as lists of offsets."""
    clusters, cluster = [], []
    for pos in [m.start() for m in SEPARATOR.finditer(text)] + [None]:
        if cluster and (pos is None or pos - cluster[-1] > CHAIN_GAP):
            clusters.append(cluster)
            cluster = []
        if pos is not None:
            cluster.append(pos)
    return clusters


def status_strings(text):
    hits = [m.start() for m in JOINED.finditer(text)] + [m.start() for m in PIPED.finditer(text)]
    return hits + [c[0] for c in separator_clusters(text) if len(c) > 1]


# T3: a separator that U6 leaves alone because it stands by itself.
def lone_separators(text):
    return [c[0] for c in separator_clusters(text) if len(c) == 1]


# U9: a badge. Structure only, so it reads the same in every language: a text
# node inside a Badge, Pill, Chip or Tag component; a short text in a pill-shaped
# element (rounded, padded); or a short ALL-CAPS word or two (letters only, so no
# ids or codes) in a span, small, sup, mark or div. Scripts without case never
# trip the last one. Whether the badge reflects real
# state is the agent's call.
CONTROL_TAGS = {
    "button", "Button", "a", "Link", "NavLink", "option", "label", "Label", "th", "td", "title",
    "MenuItem", "DropdownMenuItem", "SelectItem", "CommandItem", "TabsTrigger", "Tab",
    "h1", "h2", "h3", "h4", "h5", "h6",
}
BADGE_COMPONENTS = {"Badge", "Pill", "Chip", "Tag"}
SHORT_ELEMENT = re.compile(
    r"<(?P<tag>span|small|sup|mark|Badge|Pill|Chip|Tag)\b(?P<attrs>[^<>]*)>(?P<text>[^<>{}]{1,30})</(?P=tag)>"
)
SHORT_TEXT_NODE = re.compile(r">(?P<text>[^<>{}]{2,30})<")
LETTERS_AND_SPACES = re.compile(r"[^\W\d_]+(?: [^\W\d_]+)*")
# Where short ALL-CAPS text is a badge and not a code, an id, an acronym or a caption.
CAPS_BADGE_TAGS = {"span", "small", "sup", "mark", "div"}
PILL_CLASSES = re.compile(r"\brounded(?:-(?:md|lg|xl|2xl|full))?\b")
PADDED = re.compile(r"(?<![\w:-])px-")


def short_phrase(text):
    words = text.split()
    return 1 <= len(words) <= 4 and any(c.isalpha() for c in text)


def badges(text):
    hits = set()
    for m in SHORT_ELEMENT.finditer(text):
        if not short_phrase(m.group("text")):
            continue
        attrs = m.group("attrs")
        if m.group("tag") in BADGE_COMPONENTS or (PILL_CLASSES.search(attrs) and PADDED.search(attrs)):
            hits.add(m.start("text") - 1)
    for m in SHORT_TEXT_NODE.finditer(text):
        caps = m.group("text").strip()
        if LETTERS_AND_SPACES.fullmatch(caps) and caps.isupper() and len(caps.split()) <= 3 and len(caps.replace(" ", "")) >= 2:
            if enclosing_tag(text, m.start()) in CAPS_BADGE_TAGS:
                hits.add(m.start())
    return sorted(hits)


# U10: a small round element, or a pulse that is not a loading skeleton.
DOT_TOKEN = re.compile(r"\brounded-full\b|\banimate-(?:pulse|ping)\b")
SMALL = r"(?:1|1\.5|2|2\.5|3|px)(?![\w.])"
SMALL_SIZE = re.compile(r"(?<![\w:-])size-" + SMALL)
SMALL_H = re.compile(r"(?<![\w:-])h-" + SMALL)
SMALL_W = re.compile(r"(?<![\w:-])w-" + SMALL)
SKELETON = re.compile(r"skeleton|\bbg-(?:muted|accent|secondary|(?:gray|slate|zinc|neutral|stone)-\d)", re.I)


def status_dots(text):
    hits, seen = [], set()
    for m in DOT_TOKEN.finditer(text):
        start, end = quoted_segment(text, m.start())
        if start in seen:
            continue
        seen.add(start)
        segment = text[start:end]
        dot = "rounded-full" in segment and (
            SMALL_SIZE.search(segment) or (SMALL_H.search(segment) and SMALL_W.search(segment))
        )
        skeleton = SKELETON.search(segment) or "skeleton" in enclosing_tag(text, start).lower()
        if dot or "animate-ping" in segment or ("animate-pulse" in segment and not skeleton):
            hits.append(start)
    return hits


# U11: pictographs. Check marks and crosses (U+2713 to U+2718) are left out:
# they are usually the control or the value itself.
EMOJI = (
    "[\U0001F300-\U0001FAFF\U00002600-\U00002712\U00002719-\U000027BF\U0001F000-\U0001F2FF"
    "\U00002B50\U00002B55\U0000231A-\U0000231B\U000023E9-\U000023FA]"
)

# U11: an icon in a tinted tile. A small fixed-size box with a tinted fill and
# rounded corners whose first child is an icon. The icon-only control, an
# avatar and a tile that also holds text are not it.
CLASS_ATTR = re.compile(r"""class(?:Name)?\s*=\s*(?:"([^"]*)"|\{?\s*[`']([^`']*)[`']\s*\}?)""")
TILE_FILL = re.compile(r"(?<![\w:-])bg-(?!(?:white|transparent|black)\b)[a-z]+(?:-(?:50|100|200)\b|-\d{3}/\d{1,2}\b|/\d{1,2}\b)")
TILE_BOX = re.compile(r"(?<![\w:-])(?:size-(?:7|8|9|10|11|12)|(?:h|w)-(?:7|8|9|10|11|12))(?![\w.])")
TILE_ROUND = re.compile(r"(?<![\w:-])rounded(?:-(?:md|lg|xl|2xl|full))?(?![\w-])")
TILE_CHILD = re.compile(r"\s*>\s*<(?:svg\b|i\b|[A-Z]\w*\b[^<>]*/>)")


def icon_tiles(text):
    hits = []
    for m in CLASS_ATTR.finditer(text):
        classes = m.group(1) or m.group(2) or ""
        if TILE_FILL.search(classes) and TILE_BOX.search(classes) and TILE_ROUND.search(classes):
            if TILE_CHILD.match(text, m.end()):
                hits.append(m.start())
    return hits


# U15 and U16 run on the whole file, so a config formatted over several
# lines counts the same as a one-liner.
SCAFFOLDING = (
    r"feDropShadow|drop-shadow\(|shadowBlur|shadowColor|\bminor\s*:\s*\{"
    r"|border\s*:\s*\{[^}]*\bwidth\s*:\s*(?:[2-9]|1\.[5-9])"
    r"|grid\s*:\s*\{[^}]*\blineWidth\s*:\s*(?:[2-9]|1\.[5-9])"
)
SCAFFOLDING_PY = r"\.grid\([^)]*\b(?:linewidth|lw)\s*=\s*(?:[2-9]|1\.[5-9])|\bshadow\s*=\s*True"
LEGEND = r"legend\s*:\s*\{[^}]*\b(?:display|show)\s*:\s*true|\bshowlegend\s*:\s*true|<(?:Chart)?Legend\b"
LEGEND_PY = r"\.legend\(|\bshowlegend\s*=\s*True"

# A lone dash standing for "no value" is a table convention, not prose.
EM_DASH = re.compile(r"—|&mdash;|&#8212;|\\u2014")
LONE_DASH = re.compile(r"(?<=[\"'`>])\s*(?:—|&mdash;|&#8212;|\\u2014)\s*(?=[\"'`<])")


def em_dashes(text):
    return [m.start() for m in EM_DASH.finditer(LONE_DASH.sub(blank, text))]


# T1: an exclamation mark (! or the fullwidth ！) ending a word in visible text: a text node, a quoted
# string or a line of prose. "!==", "!important" and a bare "!" are not it.
BANG_TEXT = re.compile(r"(?<![=-])>[^<>{}\n;]*?\w(?:!(?=\s|<|$)|！)", re.M)
BANG_STRING = re.compile(r"""(["'`])[^"'`\n]*?\w[!！]\1""")
BANG_PROSE = re.compile(r"\w(?:!(?=\s|$)|！)", re.M)


def exclamations(text):
    return [m.start() for m in BANG_TEXT.finditer(text)] + [m.start() for m in BANG_STRING.finditer(text)]


def prose_exclamations(text):
    return [m.start() for m in BANG_PROSE.finditer(text)]


# T2: any uppercase styling that U1 has not already counted as an eyebrow.
UPPERCASE = re.compile(r"(?<![\w-])uppercase(?![\w-])|text-transform:\s*uppercase|textTransform:\s*[\"']uppercase")


def uppercase_text(text):
    eyebrow_spans = [(m.start(), m.end()) for m in EYEBROW.finditer(text)]
    hits = []
    for m in UPPERCASE.finditer(text):
        if any(start <= m.start() < end for start, end in eyebrow_spans):
            continue
        if enclosing_tag(text, m.start()) not in {"kbd", "abbr"}:
            hits.append(m.start())
    return hits


# Links. A link-like element is an a, a button, or a component named *Link,
# *Button or *Anchor (router-link and friends included).
LINK_NAME = r"(?:a|button|[A-Za-z.]*(?:Link|Button|Anchor)|[a-z]+(?:-[a-z]+)*-(?:link|button))"
LINK_START = re.compile(r"<(%s)(?![\w.-])" % LINK_NAME)
HIDDEN_TEXT = re.compile(r"<(\w+)\b[^<>]*\b(?:sr-only|visually-hidden|visuallyHidden)\b[^<>]*>.*?</\1>", re.S)
HAS_WORDS = re.compile(r"[^\W\d_]{2,}")
LOOKBACK = 3000


def tag_end(text, start):
    """(index after the tag that opens at start, whether it closes itself), or None. Quotes and braces are skipped."""
    depth, quote = 0, ""
    for i in range(start + 1, min(len(text), start + 2500)):
        c = text[i]
        if quote:
            if c == quote:
                quote = ""
        elif c in "\"'`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth = max(0, depth - 1)
        elif c == ">" and depth == 0:
            return i + 1, text[i - 1] == "/"
    return None


def open_element_before(text, pos, start=LINK_START):
    """Index just after the opening tag of the element (link-like by default) still open at pos, or None."""
    for m in reversed(list(start.finditer(text, max(0, pos - LOOKBACK), pos))):
        end = tag_end(text, m.start())
        if end and not end[1] and end[0] <= pos and not re.search(r"</%s\s*>" % re.escape(m.group(1)), text[end[0]:pos]):
            return end[0]
    return None


# U21: an arrow glyph (→, or ← in a right-to-left script) on a link or button, or an
# arrow icon after its text.
# An arrow that is the whole control (a Next button), one beside screen-reader
# text only, and a bare glyph in running text are not it.
ARROW = re.compile(r"[→←]|&[lr]arr;|&#859[24];|&#x219[02];")
ARROW_ICON = re.compile(r"<(?:Arrow(?:Right|Forward|LongRight)\w*|IconArrowRight\w*|MoveRight\w*)\b")
ARROW_MARKDOWN = re.compile(r"\[[^\]\n]{0,120}?[^\W\d_]\s*[→←]\s*\]\(")
STRING_OPENERS = "=:([,{?"
STRING_CLOSERS = ",)]};:/>\r\n"


def arrow_ends_string(text, arrow):
    """True when the arrow is the last thing in a string literal, as in "Learn more →"."""
    j = arrow.end()
    while j < len(text) and text[j] in " \t":
        j += 1
    if j >= len(text) or text[j] not in "\"'`":
        return False
    k = j + 1
    while k < len(text) and text[k] in " \t":
        k += 1
    if k < len(text) and text[k] not in STRING_CLOSERS:
        return False
    line_start = text.rfind("\n", 0, arrow.start()) + 1
    opening = text.rfind(text[j], max(line_start, arrow.start() - 200), arrow.start())
    if opening == -1 or not HAS_WORDS.search(text[opening + 1:arrow.start()]):
        return False
    before = text[line_start:opening].rstrip()
    return not before or before[-1] in STRING_OPENERS or before.endswith(("||", "&&", "return"))


def arrow_links(text, strings=True):
    hits = set()
    for m in ARROW.finditer(text):
        end = open_element_before(text, m.start())
        if end is not None:
            inner = re.sub(r"<[^>]*>|\{+[^{}]*\}+", " ", HIDDEN_TEXT.sub(" ", text[end:m.start()]))
            if HAS_WORDS.search(inner):
                hits.add(m.start())
                continue
        # In prose a quote mark pairs with the wrong quote, so strings are code only.
        if strings and arrow_ends_string(text, m):
            hits.add(m.start())
        line_end = text.find("\n", m.end())
        link = ARROW_MARKDOWN.search(text, max(0, m.start() - 130), len(text) if line_end == -1 else line_end)
        if link and link.start() <= m.start() < link.end():
            hits.add(m.start())
    for m in ARROW_ICON.finditer(text):
        before = text[max(0, m.start() - 200):m.start()]
        cut = before.rfind(">")
        segment = before[cut + 1:].replace('{" "}', " ")
        if cut != -1 and not re.search(r"[<{}]", segment) and HAS_WORDS.search(segment):
            hits.add(m.start())
    return sorted(hits)


def arrow_links_in_prose(text):
    return arrow_links(text, strings=False)


# U23: the same link text pointing at different places, so a screen reader
# listing the links cannot tell them apart. Words are never matched, so it works
# in any language; a single generic label ("Learn more" once) is left to the agent.
LINK_WITH_TEXT = re.compile(
    r"<(?P<tag>%s)\b(?P<attrs>(?:[^<>{}]|\{[^{}]*\})*)>(?P<text>[^<>{}]{1,80}?)</(?P=tag)>" % LINK_NAME
)
HREF = re.compile(r"""\b(?:href|to)\s*=\s*(?:"([^"]*)"|'([^']*)'|\{([^{}]*)\})""")
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]\n]{1,80})\]\(([^)\s]+)[^)]*\)")


def repeated_link_labels(text):
    links = []
    for m in LINK_WITH_TEXT.finditer(text):
        href = HREF.search(m.group("attrs"))
        links.append((m.start(), m.group("text"), next((g for g in href.groups() if g is not None), "") if href else ""))
    links += [(m.start(), m.group(1), m.group(2)) for m in MARKDOWN_LINK.finditer(text)]
    groups = {}
    for pos, label, target in links:
        label = " ".join(label.split()).casefold()
        if HAS_WORDS.search(label):
            groups.setdefault(label, []).append((pos, target))
    hits = []
    for items in groups.values():
        if len(items) > 1 and len({target for _, target in items}) > 1:
            hits += [pos for pos, _ in sorted(items)[1:]]
    return sorted(hits)


# U26: a colored border of 3px or more on the left edge of a box. A neutral
# gray bar, a 1px or 2px rule (quotes, blockquotes) and a border on every edge
# are not it.
EDGE_UTILITY = re.compile(r"(?<![\w-])border-[ls]-(?:4|8|\[(?:[3-9]|\d{2,})px\])(?![\w-])")
EDGE_COLOR = re.compile(
    r"(?<![\w-])border-(?:[ls]-)?(?:"
    r"\[(?:#|rgb|hsl|oklch|var\()[^\]]*\]"
    r"|(?!(?:[lrtbxyse](?:-|(?![\w-]))|solid|dashed|dotted|double|hidden|none|border|input|muted|transparent|current"
    r"|collapse|separate|spacing|opacity)(?![\w-]))(?!(?:gray|slate|zinc|neutral|stone)-)(?!\d|\[)"
    r"[a-z]+(?:-\d{2,3})?(?:/\d+)?"
    r")(?![\w-])"
)
EDGE_DECLARATION = re.compile(
    r"\b(?:border-(?:left|inline-start)|borderLeft|borderInlineStart)\s*:\s*[\"'`]?(?:[3-9]|\d{2,})px\s+solid\s+"
    r"(?P<color>[^;}\s\"'`(]+(?:\([^)]*\))?)"
)
NEUTRAL_NAMES = {"transparent", "black", "white", "gray", "grey", "silver", "currentcolor", "inherit"}


def neutral_color(value):
    value = value.lower()
    if value in NEUTRAL_NAMES or re.match(r"(?:gray|grey|slate|zinc|neutral|stone)", value):
        return True
    hexa = re.match(r"#([0-9a-f]{3}|[0-9a-f]{6})\b", value)
    if hexa:
        digits = hexa.group(1)
        digits = "".join(c * 2 for c in digits) if len(digits) == 3 else digits
        channels = [int(digits[i:i + 2], 16) for i in (0, 2, 4)]
        return max(channels) - min(channels) <= 16
    rgb = re.match(r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)", value)
    if rgb:
        channels = [int(c) for c in rgb.groups()]
        return max(channels) - min(channels) <= 16
    return False


def edge_bars(text):
    hits, seen = [], set()
    for m in EDGE_UTILITY.finditer(text):
        start, end = quoted_segment(text, m.start())
        if start not in seen and EDGE_COLOR.search(text[start:end]):
            seen.add(start)
            hits.append(start)
    return hits + [m.start() for m in EDGE_DECLARATION.finditer(text) if not neutral_color(m.group("color"))]


# U18: odd pixel values, and anything over 16 that is not a multiple of 4.
# 2, 6, 10 and 14 are Tailwind's half steps (0.5, 1.5, 2.5, 3.5).
SPACING = re.compile(
    r"(?<![\w-])-?(?:[mp][trblxyse]?|gap(?:-[xy])?|space-[xy])-\[(-?\d+(?:\.\d+)?)px\]"
)
# A shorthand declaration carries several values ("padding: 8px 18px");
# every px in it is checked, where a first-value-only pattern saw none.
SPACING_DECL = re.compile(
    r"\b(?:margin|padding)(?:-(?:top|right|bottom|left))?\s*:\s*([^;}\n]+)"
    r"|\bgap\s*:\s*([^;}\n]+)",
    re.M,
)
PX_VALUE = re.compile(r"-?\d+(?:\.\d+)?px")


def off_scale_value(value):
    return bool(value % 2 or (value > 16 and value % 4))


def off_scale(text):
    hits = []
    for m in SPACING.finditer(text):
        if off_scale_value(float(m.group(1))):
            hits.append(m.start())
    for m in SPACING_DECL.finditer(text):
        values = m.group(1) if m.group(1) is not None else m.group(2)
        for v in PX_VALUE.finditer(values):
            if off_scale_value(float(v.group(0)[:-2])):
                hits.append(m.start())
    return hits


MARKUP = {"markup", "prose"}
RULES = [
    ("U1 eyebrow", eyebrows, MARKUP | {"style"}),
    ("U2 decorative numbering", numbering, {"markup"}),
    ("U2 decorative numbering", rx(NUMBERING_PROSE), {"prose"}),
    ("U6 status string", status_strings, TEXT),
    ("U9 badge", badges, {"markup"}),
    ("U10 status dot", status_dots, MARKUP),
    ("U11 emoji", rx(EMOJI), ALL),
    ("U11 icon tile", icon_tiles, MARKUP),
    ("U15 chart scaffolding", rx(SCAFFOLDING), MARKUP),
    ("U15 chart scaffolding", rx(SCAFFOLDING_PY), {"python"}),
    ("U16 legend", rx(LEGEND), MARKUP),
    ("U16 legend", rx(LEGEND_PY), {"python"}),
    ("U21 arrow link", arrow_links, {"markup", "data", "python"}),
    ("U21 arrow link", arrow_links_in_prose, {"prose"}),
    ("U23 repeated link label", repeated_link_labels, {"markup", "prose"}),
    ("unslop 13 em dash", em_dashes, TEXT),
]
STYLED = MARKUP | {"style"}
# Counted only when the taste file bans them.
TASTE_RULES = {
    "exclamation": [
        ("T1 exclamation mark", exclamations, {"markup", "data", "python"}),
        ("T1 exclamation mark", prose_exclamations, {"prose"}),
    ],
    "uppercase": [("T2 uppercase text", uppercase_text, MARKUP | {"style"})],
    "middle dot": [("T3 middle dot", lone_separators, TEXT)],
}
# Words in a ban line that select a counted rule. Other bans are read by the agent.
TASTE_WORDS = {
    "exclamation": "exclamation",
    "uppercase": "uppercase|all caps|all-caps",
    "middle dot": "middle.?dot|bullet separator|separator",
}
TASTE_FILE = os.path.join(".unslop-ui", "taste.md")
OFF_LEAD = re.compile(r"\s*(U\d{1,2}|T\d{1,2}|unslop \d{1,2})\b\s*(?:,|and\b|&|\+)?")
SURFACE_RULES = [
    ("U17 gradient or glow", rx(
        r"\bbg-(?:gradient|linear|radial|conic)-to?-?|(?:linear|radial|conic)-gradient\(|\bbg-clip-text\b|background-clip:\s*text"
        r"|\bblur-(?:2xl|3xl)\b|\bshadow-\[0_0_|\bshadow-[a-z]+-\d{2,3}(?:/\d+)?\b|box-shadow:[^;]*\b0\s+0\s+\d+px"
    ), STYLED),
    ("U18 off-scale spacing", off_scale, STYLED),
    ("U19 extra-heavy weight", rx(
        r"\bfont-(?:extrabold|black)\b|font-?[wW]eight\W{0,3}[89]00\b|\bfont-\[[89]00\]"
    ), STYLED),
    ("U20 motion", rx(
        r"\btransition-all\b|transition:\s*all\b|\bhover:scale-|\banimate-bounce\b|\bwhileInView\b|\bdata-aos\b"
    ), STYLED),
    ("U26 edge accent bar", edge_bars, STYLED),
]


def iter_files(targets):
    for target in targets:
        if os.path.isfile(target):
            yield target
            continue
        for root, dirs, files in os.walk(target):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                if name in SKIP_FILES or ".min." in name:
                    continue
                if os.path.splitext(name)[1].lower() in KIND_OF:
                    yield os.path.join(root, name)


def off_ids(line):
    """The rule ids a bullet of the Off section starts with: "U11, our names use emoji" is {"u11"}."""
    body, pos, ids = re.sub(r"^\s*[-*]\s+", "", line), 0, set()
    while True:
        m = OFF_LEAD.match(body, pos)
        if not m:
            return ids
        ids.add(m.group(1).lower())
        pos = m.end()


def read_taste(path):
    """(bans, off) from a taste file: the counted rules its Bans section switches on, and the rule ids its Off section lists."""
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            text = f.read()
    except OSError:
        return set(), set()

    def bullets(heading):
        section = re.search(r"^##\s+%s\s*$(.*?)(?=^##\s|\Z)" % heading, text, re.M | re.S | re.I)
        return [l for l in (section.group(1) if section else "").splitlines() if re.match(r"\s*[-*]\s+\S", l)]

    bans = {key for key, words in TASTE_WORDS.items() if any(re.search(words, l, re.I) for l in bullets("Bans"))}
    return bans, {rule for line in bullets("Off") for rule in off_ids(line)}


def rule_id(name):
    """"U11 emoji" is U11, "unslop 13 em dash" is "unslop 13"."""
    parts = name.lower().split()
    return " ".join(parts[:2]) if parts[0] == "unslop" else parts[0]


def count(targets, surface=False, bans=(), off=()):
    rules = RULES + (SURFACE_RULES if surface else [])
    for key in TASTE_WORDS:
        if key in bans:
            rules = rules + TASTE_RULES[key]
    rules = [rule for rule in rules if rule_id(rule[0]) not in off]
    results = {name: {"count": 0, "examples": []} for name, _, _ in rules}
    self_path = os.path.abspath(__file__)
    for path in iter_files(targets):
        # The counter's own patterns are slop-shaped text; never count itself.
        if os.path.abspath(path) == self_path:
            continue
        # A file named on the command line is scanned whatever its extension.
        kind = KIND_OF.get(os.path.splitext(path)[1].lower(), "markup")
        try:
            if os.path.getsize(path) > MAX_BYTES:
                continue
            with open(path, encoding="utf-8", errors="replace") as f:
                text = strip_comments(f.read(), kind)
        except OSError as e:
            print("Skipped {}: {}".format(path, e), file=sys.stderr)
            continue
        line_starts = [m.end() for m in re.finditer(r"\n", text)]
        for name, find, kinds in rules:
            if kind not in kinds:
                continue
            entry = results[name]
            for pos in sorted(find(text)):
                entry["count"] += 1
                if len(entry["examples"]) < MAX_EXAMPLES:
                    entry["examples"].append("{}:{}".format(path, bisect.bisect_right(line_starts, pos) + 1))
    results["total"] = sum(r["count"] for r in results.values())
    return results


def display_id(rule):
    return rule if rule.startswith("unslop") else rule.upper()


def escape(value, prop=False):
    """GitHub workflow command escaping: data always, property values also escape ':' and ','."""
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return value.replace(":", "%3A").replace(",", "%2C") if prop else value


def annotations(results):
    """GitHub workflow commands for the examples the counter kept, then a summary line."""
    lines = []
    for rule, entry in results.items():
        if rule == "total":
            continue
        for example in entry["examples"]:
            path, _, line = example.rpartition(":")
            if os.path.isabs(path):
                path = os.path.relpath(path)
            lines.append("::warning file={},line={},title={}::Possible AI tell. Read it and keep it if it earns its place.".format(
                escape(path[2:] if path.startswith("./") else path, True), line, escape(rule, True)))
    lines.append("unslop-ui: {} possible tells".format(results["total"]))
    return lines


def main():
    parser = argparse.ArgumentParser(description="Count UI slop candidates in files or folders.")
    parser.add_argument("targets", nargs="+", metavar="file-or-folder")
    parser.add_argument("--surface", action="store_true", help="also count U17 to U20 and U26")
    parser.add_argument("--max", type=int, metavar="N", help="exit 1 when the total is above N")
    parser.add_argument("--taste", metavar="PATH", help="taste file to read (default: {})".format(TASTE_FILE))
    parser.add_argument("--format", choices=("json", "github"), default="json", help="json (default) or github workflow annotations")
    args = parser.parse_args()

    missing = [t for t in args.targets + ([args.taste] if args.taste else []) if not os.path.exists(t)]
    if missing:
        print("Not found: " + ", ".join(missing), file=sys.stderr)
        sys.exit(2)

    bans, off = read_taste(args.taste or TASTE_FILE)
    if off:
        print("Off by taste file: " + ", ".join(sorted(display_id(rule) for rule in off)), file=sys.stderr)
    results = count(args.targets, args.surface, bans, off)
    if args.format == "github":
        print("\n".join(annotations(results)))
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    if args.max is not None and results["total"] > args.max:
        sys.exit(1)


if __name__ == "__main__":
    main()
