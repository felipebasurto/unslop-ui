# Finding tells

Candidate searches for step 1 of the procedure. Run each with Grep (ripgrep syntax) over the target, skipping `node_modules`, build output and lockfiles. A hit is a candidate, not a verdict: read the line, apply the rule, and keep what earns its place. Run the same searches again after editing so the two counts compare.

These patterns look at structure (classes, markup, glyphs, chart config), never at words, so they behave the same on copy in any language and script. What a string means is for you to read.

Count a hit once per element or string, not once per match.

## Copy and decoration

- **U1 eyebrow.** `uppercase.{0,200}tracking-(wide|wider|widest|\[)` or `tracking-(wide|wider|widest|\[).{0,200}uppercase` or `text-transform:\s*uppercase`. Table headers and key caps use the same styling and are not eyebrows. A pill with a dot above a heading is.
- **U2 numbering.** `>\s*0[1-9]\s*<`, `['"]0[1-9]['"]`, `>[^<>{}]*//[^<>]*<`, `padStart\(\s*2\s*,\s*['"]0['"]`. Dates and times ("01/02", "01:30") are not numbering. Inside an `<ol>` the order is real: skip it. Real step order stays.
- **U6 status string.** Two or more of `·`, `•`, `&middot;`, `&bull;` within a few lines, `join\(\s*['"]\s*(·|•|\|)\s*['"]\s*\)`, `>[^<>{}]*\s\|\s[^<>{}]*\s\|\s[^<>{}]*<`. One separator ("Jan 3 · 14:02") is ordinary punctuation.
- **U9 badge.** Text inside a badge-shaped element: `<(Badge|Pill|Chip|Tag)\b[^>]*>[^<{]{1,30}<`; a short text in a `span`, `small`, `sup` or `mark` that is both rounded and padded (`rounded` and `px-` in the same tag); a short ALL-CAPS text node, `>\s*[\p{Lu}][\p{Lu} ]{1,28}<` with `rg -P`, which never matches a script without case. Skip a button, link, menu item, tab, table cell and heading. Keep it if it renders from a condition or a value.
- **U10 status dot.** `animate-(pulse|ping)`, `rounded-full` on an element of `size-1` to `size-3` (or `h-`/`w-` 1 to 3, `px`). A pulsing loading skeleton is not a status dot. Keep a dot bound to a real status.
- **U11 emoji.** Grep with `-P` for `[\x{1F300}-\x{1FAFF}\x{2600}-\x{2712}\x{2719}-\x{27BF}\x{2B50}\x{2B55}]`. Also look for an icon in a tinted tile: `bg-\w+-(50|100|200)` or `bg-\w+/\d+` with `size-(8|9|10|11|12)` or `h-(8|9|10|11|12)` and `rounded`, whose first child is an icon.
- **unslop 13 em dash.** `—|&mdash;|&#8212;|\\u2014`. A lone "—" standing for an empty value stays.

## Links and actions

- **U21 arrow link.** `[→←]|&[lr]arr;|&#859[24];` (← only in a right-to-left script) at the end of the text of an `a`, `Link`, `button` or `Button`, or in a string that ends with it ("Learn more →"); `<(ArrowRight|IconArrowRight|MoveRight)\w*` after text in the same element. Skip an icon-only control, a bare glyph with no text before it, `↗` and an arrow between two links. In Markdown only `[text →](url)` counts; an arrow in running text is not it.
- **U23 repeated link text.** List the links (`<a ...>text</a>`, `<Link ...>text</Link>`, `<Button ...>text</Button>`, `[text](url)`) and look for the same text, ignoring case and spacing, with different `href`s. The same text with the same `href` is fine. A lone generic name ("Click here") needs your reading.

## Charts

- **U15 scaffolding.** `feDropShadow|drop-shadow\(|shadowBlur|shadowColor`, `minor\s*:\s*\{`, a `border` or `grid` option with `width` or `lineWidth` of 1.5 or more; in Python `\.grid\(.*(linewidth|lw)\s*=\s*([2-9]|1\.[5-9])`, `shadow\s*=\s*True`. Thin the scaffolding. Do not change the chart type, data or series colors.
- **U16 legend.** `legend\s*:\s*\{[^}]*(display|show)\s*:\s*true`, `showlegend\s*:\s*true`, `<(Chart)?Legend\b`; in Python `\.legend\(`. Keep a legend for more than four series.

## Surface (only with `--surface`)

- **U17 gradient or glow.** `bg-(gradient|linear|radial|conic)-to?-`, `(linear|radial|conic)-gradient\(`, `bg-clip-text`, `background-clip:\s*text`, `blur-(2xl|3xl)`, `shadow-\[0_0_`, `shadow-[a-z]+-\d{2,3}`, `box-shadow:[^;]*\b0\s+0\s+\d+px`
- **U18 off-scale spacing.** `-?(m|p)[trblxyse]?-\[\d+px\]`, `(gap|space)(-[xy])?-\[\d+px\]`, `(margin|padding)[a-z-]*:\s*\d+px`, `gap:\s*\d+px`; a hit counts when the value is odd, or above 16 and not a multiple of 4
- **U19 heavy weight.** `font-(extrabold|black)`, `font-?[wW]eight\W{0,3}[89]00`, `font-\[[89]00\]`
- **U20 motion.** `transition-all`, `transition:\s*all`, `hover:scale-`, `animate-bounce`, `whileInView`, `data-aos`
- **U26 edge accent bar.** `border-[ls]-(4|8|\[[3-9]px\])` in a class string that also has a colored `border-<color>` (not gray, slate, zinc, neutral, stone, border or transparent), and `border-(left|inline-start):\s*([3-9]|\d\d)px\s+solid\s+(?!transparent)`. Skip 1px and 2px rules, a gray bar and a border on every edge. Keep a bar on a real status (`role="alert"`).

## Taste bans (only when `.unslop-ui/taste.md` bans them)

- **T1 exclamation mark.** `\w(!(\s|<|$)|！)` in a text node, a quoted string or a line of prose. `!==`, `!important` and a bare `!` are not it.
- **T2 uppercase text.** `(?<![\w-])uppercase(?![\w-])`, `text-transform:\s*uppercase`. Skip `kbd` and `abbr`, and skip what U1 already counted as an eyebrow.
- **T3 middle dot.** A single `·`, `•`, `&middot;` or `&bull;` that stands alone. Two or more close together are U6.

## What no pattern finds

Anything that depends on what words mean needs reading, in whatever language the copy is in: U3 subtitles, U4 botsplaining, U5 leaked design notes, U7 labeling everything, U8 slogans, U12 chart titles that name the chart, U13 reading instructions, U14 saying it twice, U22 one action with several names, U23 generic names, U24 equal stat cards, U25 missing states and filler words. Read every visible string and tag each problem yourself.
