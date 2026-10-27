<h1 align="center">unslop-ui</h1>

<p align="center">An agent skill that strips the AI look out of interface and chart copy.</p>

<p align="center">
  <a href="https://github.com/felipebasurto/unslop-ui/actions/workflows/test.yml"><img src="https://github.com/felipebasurto/unslop-ui/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/format-Agent%20Skills-555" alt="Agent Skills format"></a>
</p>

![A landing page with eleven AI tells tagged by rule id, next to the same page after /unslop-ui](assets/anatomy.svg)

Agents decorate everything they build: a tiny uppercase label over every heading, `01 //` before each feature, a subtitle that repeats the title, a caption explaining the button you are looking at, a green "LIVE" dot wired to nothing. `unslop-ui` finds those patterns, removes them, and tells you what it cut and what it left for you to decide.

It is the interface companion to [`/pstack:unslop`](https://github.com/cursor/plugins/tree/main/pstack), which cleans prose. `unslop-ui` loads unslop's rules when it runs and applies them to every string it keeps.

## What it removes

| Id | Pattern | Example |
|---|---|---|
| U1 | Eyebrow labels | `INTRODUCING LEDGER` above the H1 |
| U2 | Decorative numbering | `01 //`, `02 //` on features with no real order |
| U3 | Subtitle reflex | "Analytics" with "Understand your data better" under it |
| U4 | Botsplaining | "Click the button above to get started" |
| U5 | Leaked design notes | "(updates in real time)", "This card shows..." |
| U6 | Status strings | `Live · v2.4 · Synced · Updated just now` |
| U7 | Labeling everything | Label, placeholder and helper text that all say "email" |
| U8 | Staccato slogans | "Finance. Simplified. Finally." |
| U9 | Badges without state | `NEW`, `AI`, `Beta` added for flavor |
| U10 | Status dots | `animate-pulse` dot next to static data |
| U11 | Decorative emojis | `🚀 Get started`, `💰 Revenue` |
| U12 | Chart titles that name the chart | "Line chart of weekly active users" |
| U13 | Reading instructions | "Each point represents one week. Hover for details." |
| U14 | Saying it twice | `▲ 12% up` plus "Revenue grew 12% compared to last month" |

It leaves logic, data, colors and layout alone. It keeps `aria-label`, `alt` and screen-reader text, and moves a cut label into `aria-label` when it was the only accessible name. Anything that reflects real state (a live connection, a real step order) stays, and the report says why.

## Examples

All three come from [`examples/`](examples): the files in `before/` were written to be full of tells, and `after/` is the unedited output of one `/unslop-ui` run in a fresh Claude Code session. The drawings show those files rendered with sample data, and each tell carries the id of the rule that removed it.

### A dashboard

![A dashboard before and after: the eyebrow, subtitle, emojis, Live dot, self-describing captions and status string are gone](assets/dashboard.svg)

<details>
<summary>See the code change</summary>

```diff
-  <p className="... uppercase tracking-[0.2em] ...">Overview</p>
   <h1 className="text-2xl font-semibold">Dashboard</h1>
-  <p className="text-muted-foreground">A real-time overview of your key business metrics, all in one place.</p>

-  <CardTitle>💰 Total revenue</CardTitle>
+  <CardTitle>Total revenue</CardTitle>
-  <span className="text-green-600">▲ 12% up</span>
-  <CardDescription>Revenue grew 12% compared to last month, showing strong momentum.</CardDescription>
+  <span className="text-green-600">+12% vs last month</span>

-  <span ...><span className="size-2 rounded-full bg-emerald-500 animate-ping" />Live</span>
-  <CardDescription>This card shows the number of users active right now (updates in real time).</CardDescription>

-  <span className="text-xs">Last 30 days · All plans · Excl. trials</span>
+  <span className="text-xs">Last 30 days</span>
```

Full files: [before](examples/before/Dashboard.tsx), [after](examples/after/Dashboard.tsx).

</details>

### A chart

![A line chart before and after: the title names the metric, the reading instructions, legend and per-point labels are gone](assets/chart.svg)

<details>
<summary>See the code change</summary>

```diff
-  title: { display: true, text: "📈 Line chart of weekly active users" },
-  subtitle: { display: true, text: "Each point represents one week — hover over a point to see the exact value." },
-  legend: { display: true },
-  datalabels: { display: true },
+  title: { display: true, text: "Weekly active users" },
+  legend: { display: false },
```

Full files: [before](examples/before/chart.js), [after](examples/after/chart.js).

</details>

### A landing page

The page from the drawing at the top, rendered in a browser. Full files: [before](examples/before/landing.html), [after](examples/after/landing.html).

![The landing example rendered before and after](assets/before-after.png)

### By the numbers

![Bar chart: the counter finds 26 tells in examples/before and 0 after one run](assets/counts.svg)

The counter only sees the patterns a regex can find. The run also removed 12 tells it can't see (subtitles, botsplaining, slogans, chart titles), counted by reading.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills), for Claude Code, Cursor, Codex and other agents:

```bash
npx skills add felipebasurto/unslop-ui -g
```

As a Claude Code plugin:

```bash
claude plugin marketplace add felipebasurto/unslop-ui
```

```bash
claude plugin install unslop-ui@unslop-ui
```

By hand:

```bash
git clone https://github.com/felipebasurto/unslop-ui && cp -R unslop-ui/skills/unslop-ui ~/.claude/skills/
```

For the full effect, install [pstack](https://github.com/cursor/plugins/tree/main/pstack) too. Without it, `unslop-ui` falls back to a short list of prose rules.

## Use

```
/unslop-ui src/pages/landing.tsx
```

Pass a file, a folder or a component name. With no argument it works on the files changed in the conversation. As a Claude Code plugin the command is `/unslop-ui:unslop-ui`. In Codex, type `$unslop-ui`.

The skill only runs when you call it. It never triggers on its own, because cutting copy is a decision you should make.

Each run ends with a report:

| Rule | Before | After |
|---|---|---|
| U1 eyebrow | 5 | 0 |
| U2 decorative numbering | 3 | 0 |
| unslop 13 em dash | 3 | 0 |

followed by what it kept on purpose and what needs your decision, such as a status dot that might be wired to real data.

## The counter

`scripts/count_tells.py` is a regex counter for the patterns that can be found mechanically (U1, U2, U6, U9, U10, U11 and em dashes). The skill runs it before and after editing. You can run it on its own, in CI for example:

```bash
python3 skills/unslop-ui/scripts/count_tells.py src/
```

It prints JSON with a count and up to five `file:line` locations per rule. It is a heuristic: it catches candidates, misses the patterns that need reading (U3 to U5, U7, U8, U12, U13) and flags some legitimate cases.

## Compatibility

| Agent | Status |
|---|---|
| Claude Code | Full support: loads unslop rules automatically, takes arguments |
| Cursor | Works. Run `scripts/load_unslop.py` yourself if the unslop rules don't appear |
| Codex | Works, explicit invocation only (`agents/openai.yaml`) |

The counter needs Python 3.9 or newer and no packages.

## Development

```bash
python3 -m unittest discover -s tests
```

The tests check that the counter finds every planted pattern in `examples/before`, finds none in `examples/after`, ignores code comments, and that the loader picks the newest pstack install or falls back cleanly.

## Credits

The unslop rules are by [Lauren Tan](https://github.com/poteto), from [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). The UI patterns come from what designers and developers keep pointing out about AI-built interfaces in 2026.

## License

[MIT](LICENSE)
