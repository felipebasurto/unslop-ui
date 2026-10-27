---
name: unslop-ui
description: "Cut AI tells from interface and chart copy: eyebrow labels, 01/02/03 numbering, redundant subtitles, captions that explain what is already visible, leaked design notes, decorative badges, status dots, chart clutter and legends a direct label could replace. Applies /pstack:unslop to every string it keeps."
disable-model-invocation: true
argument-hint: "[file, folder or component]"
allowed-tools: Bash(python3 *)
---

# Unslop UI

Edit the visible text and decorative chrome of a web page, app screen, chart or dashboard so it stops reading as AI-generated. A good interface is used, not read: keep the words a person needs to act, and cut the rest.

Target: $ARGUMENTS (if empty, use the files changed in this conversation, or ask).

## Writing rules from /pstack:unslop

Apply these to every string you keep. Cite them by their number.

!`python3 ${CLAUDE_SKILL_DIR}/scripts/load_unslop.py`

If the line above still shows a command instead of rules (agents other than Claude Code), run `python3 scripts/load_unslop.py` from this skill's folder and apply what it prints.

## UI rules

Ids are stable. Cite them as U1 to U16 in the report.

### Interface copy

- **U1. Eyebrow labels.** Small uppercase or letter-spaced text above a heading ("PASSPORT", "FEATURES", "HOW IT WORKS"). Delete it. The heading already says what the section is.
- **U2. Decorative numbering.** "01 02 03", "01 // Features", "§", "//" prefixes. Delete unless the order is real and the user follows it (steps of a checkout, a numbered install guide).
- **U3. Subtitle reflex.** A subtitle under every heading, or a line above the H1. Keep one only when it states a fact the heading doesn't. "Analytics / Understand your data better" loses the second line.
- **U4. Botsplaining.** Captions, helper text and descriptions that narrate what the element visibly does ("Click the button below to get started", "This chart shows revenue over time"). Delete. Headings and captions stay at 5 words or fewer. Exempt: empty states, error messages, and confirmations of destructive actions, which may use a full sentence.
- **U5. Leaked design notes.** Text about how the screen works or why it was designed that way, long parentheticals, "(updates in real time)", "(powered by AI)". Delete it, or move it to a tooltip if a user would genuinely look for it.
- **U6. Status strings.** Facts chained with "·" or "|" ("12 items · Updated 2m ago · Synced · v2.1"). Keep the one fact the user acts on. Put others where they're needed, or drop them.
- **U7. Labeling everything.** A label that repeats the placeholder, the icon, the button text, or the section heading. Pick one cue. A search field with a magnifier icon needs neither a "Search" label nor a "Search..." placeholder beyond one of them.
- **U8. Staccato and empty slogans.** "One. Big. Thing.", "Built different.", "Ship faster. Think less." Rewrite as one sentence that names the thing and what it does, or delete.

### Decoration

- **U9. Badges and pills without real state.** "LIVE", "NEW", "AI", "Beta", "Pro", "🔥 Popular" added for flavor. Keep a badge only if it reflects data the app actually tracks (a real stream is live, an item is actually new since the last visit).
- **U10. Status dots.** Pulsing or colored dots (`animate-pulse`, small `rounded-full` dots) next to text. Keep only if bound to a real live status.
- **U11. Decorative emojis and icons.** In headings, buttons, KPI labels and list items. Delete. An icon stays only if it is the control itself (icon button with an `aria-label`) or if it carries meaning the text does not.

### Charts and dashboards

- **U12. Chart titles that name the chart type.** "Bar chart of monthly revenue" becomes "Monthly revenue", or the finding: "Revenue doubled since March".
- **U13. Reading instructions.** Subtitles or captions that explain how to read the chart ("Each bar represents one month", "Hover for details"). Delete.
- **U14. Saying it twice.** Each quantity gets one encoding. A bar, a number on the bar, a gridline at its height and an axis tick all saying the same value is three too many; a KPI with arrow plus percent plus the word "up" plus a sentence under it ("Revenue grew 12% compared to last month") is the same mistake in text. Keep the encoding the reader needs: axis and gridlines for shape, a printed value for the number that matters (often only the last point or the max).
- **U15. Chart scaffolding that competes with the data.** A frame box around the plot area, dark or dense gridlines, minor ticks, thick axis borders, 3D, drop shadows and glows on marks, background fills behind the plot. Delete them, or make what must stay (a few gridlines, one baseline) a hairline in a light gray. Data on top, labels next, scaffolding faintest. Do not redesign the chart: same type, same data, same series colors.
- **U16. Legend where a direct label works.** A legend box that makes the reader match colors to names, when the name could sit at the end of the line or next to the bar. Label the series directly, ideally with its latest value ("This year 1,150"), and remove the legend. Keep a legend for more than four series or when the marks are too close to label.

For before/after pairs, read [references/examples.md](references/examples.md) when unsure how far to cut.

## Guardrails

- Change visible text and decorative elements only. Do not touch logic, data, colors, spacing tokens or layout structure. The one exception is chart scaffolding under U15, which may be thinned or lightened.
- When you delete an element, delete its now-empty wrapper and any margin or gap that existed only for it. A wrapper left holding a single child it only existed to group goes too.
- Never delete `aria-label`, `alt`, `title` on icon buttons, or screen-reader-only text. If cut visible text was the only accessible name, move it into `aria-label`.
- Text that comes from data, props, i18n files or a CMS: edit it at its source (the translation file, the fixture) or report it, don't hard-code a replacement in the component.
- If a flagged case earns its place (real state, real order, legal text), keep it and say why in the report.

## Procedure

Copy this checklist and track it:

```
- [ ] 1. Count: python3 ${CLAUDE_SKILL_DIR}/scripts/count_tells.py <target>   (${CLAUDE_SKILL_DIR} is this file's folder)
- [ ] 2. Read every visible string and decorative element; tag each problem with U1-U16 or an unslop rule number
- [ ] 3. Edit
- [ ] 4. Count again with the same command
- [ ] 5. Report
```

The counter is a regex heuristic. It finds candidates and gives a before/after number. It misses U3, U4, U5, U7, U8, U12, U13 and U14, which need reading. For U15 and U16 it only sees the code forms (shadows, thick axis borders and gridlines, legends turned on). It also flags some legitimate cases. Your reading in step 2 is the real check.

Report format:

| Rule | Before | After |
|---|---|---|
| U1 eyebrow | 6 | 0 |
| unslop 13 em dash | 4 | 0 |

Then list what you kept on purpose, one line each, with the reason.
