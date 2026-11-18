# Finding tells

Candidate searches for step 1 of the procedure. Run each with Grep (ripgrep syntax) over the target, skipping `node_modules`, build output and lockfiles. A hit is a candidate, not a verdict: read the line, apply the rule, and keep what earns its place. Run the same searches again after editing so the two counts compare.

Count a hit once per element or string, not once per match.

## Copy and decoration

- **U1 eyebrow.** `uppercase.{0,200}tracking-(wide|wider|widest|\[)` or `tracking-(wide|wider|widest|\[).{0,200}uppercase` or `text-transform:\s*uppercase`. Table headers and key caps use the same styling and are not eyebrows. A pill with a dot above a heading is.
- **U2 numbering.** `>\s*0[1-9]\s*<`, `['"]0[1-9]['"]`, `>[^<>{}]*//[^<>]*<`, `padStart\(\s*2\s*,\s*['"]0['"]`. Dates and times ("01/02", "01:30") are not numbering. Real step order stays.
- **U6 status string.** Two or more of `·`, `•`, `&middot;`, `&bull;` within a few lines, `join\(\s*['"]\s*(·|•|\|)\s*['"]\s*\)`, `>[^<>{}]*\s\|\s[^<>{}]*\s\|\s[^<>{}]*<`. One separator ("Jan 3 · 14:02") is ordinary punctuation.
- **U9 badge.** `>\s*(LIVE|NEW|BETA|AI|PRO|HOT)\s*<`, `>\s*(Popular|Most popular|Coming soon|Featured|Trending|AI-powered|Powered by AI)\s*<`, `['"](LIVE|NEW|BETA|HOT)['"]`. Not inside a button, link, menu item, tab or heading. Keep it if it renders from a condition or a value.
- **U10 status dot.** `animate-(pulse|ping)`, `rounded-full` on an element of `size-1` to `size-3` (or `h-`/`w-` 1 to 3, `px`). A pulsing loading skeleton is not a status dot. Keep a dot bound to a real status.
- **U11 emoji.** Grep with `-P` for `[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B50}\x{2B55}]`. Also look for an icon in a tinted tile: `bg-\w+-(50|100|200)` or `bg-\w+/\d+` with `size-(8|9|10|11|12)` or `h-(8|9|10|11|12)` and `rounded`, whose first child is an icon.
- **unslop 13 em dash.** `—|&mdash;|&#8212;|\\u2014`. A lone "—" standing for an empty value stays.

## Charts

- **U12 chart-type title.** `(?i)\b(bar|line|pie|area|scatter|donut|column) (chart|graph|plot) (of|showing|for)\b`. Live data keeps a neutral title.
- **U13 reading instructions.** `(?i)\beach (bar|point|dot|line|slice|column|row) (represents|shows|is)\b`, `(?i)\bhover (over|for|to see)\b`. One hit per sentence.
- **U15 scaffolding.** `feDropShadow|drop-shadow\(|shadowBlur|shadowColor`, `minor\s*:\s*\{`, a `border` or `grid` option with `width` or `lineWidth` of 1.5 or more; in Python `\.grid\(.*(linewidth|lw)\s*=\s*([2-9]|1\.[5-9])`, `shadow\s*=\s*True`. Thin the scaffolding. Do not change the chart type, data or series colors.
- **U16 legend.** `legend\s*:\s*\{[^}]*(display|show)\s*:\s*true`, `showlegend\s*:\s*true`, `<(Chart)?Legend\b`; in Python `\.legend\(`. Keep a legend for more than four series.

## Surface (only with `--surface`)

- **U17 gradient or glow.** `bg-(gradient|linear|radial|conic)-to?-`, `(linear|radial|conic)-gradient\(`, `bg-clip-text`, `background-clip:\s*text`, `blur-(2xl|3xl)`, `shadow-\[0_0_`, `shadow-[a-z]+-\d{2,3}`, `box-shadow:[^;]*\b0\s+0\s+\d+px`
- **U18 off-scale spacing.** `-?(m|p)[trblxyse]?-\[\d+px\]`, `(gap|space)(-[xy])?-\[\d+px\]`, `(margin|padding)[a-z-]*:\s*\d+px`, `gap:\s*\d+px`; a hit counts when the value is odd, or above 16 and not a multiple of 4
- **U19 heavy weight.** `font-(extrabold|black)`, `font-?[wW]eight\W{0,3}[89]00`, `font-\[[89]00\]`
- **U20 motion.** `transition-all`, `transition:\s*all`, `hover:scale-`, `animate-bounce`

## What no pattern finds

U3 subtitles, U4 botsplaining, U5 leaked design notes, U7 labeling everything, U8 slogans and U14 saying it twice need reading. Read every visible string and tag each problem yourself.
