# unslop-ui

An agent skill that removes the text and decoration that make an interface look AI-generated: eyebrow labels over every heading, `01 // 02 // 03` numbering, subtitles nobody needs, captions that explain what is already on screen, "LIVE" badges and pulsing dots that track nothing.

It is the interface companion to [`/pstack:unslop`](https://github.com/cursor/plugins/tree/main/pstack), which cleans prose. `unslop-ui` loads unslop's rules when it runs and applies them to every string it keeps.

![The same landing page before and after running /unslop-ui](assets/before-after.png)

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

## Examples

[`examples/before`](examples/before) holds a landing page, a React dashboard and a Chart.js config full of these patterns. [`examples/after`](examples/after) is the unedited output of one `/unslop-ui` run on them in a fresh Claude Code session.

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
