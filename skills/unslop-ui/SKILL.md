---
name: unslop-ui
description: "Cut AI tells from interface and chart copy: eyebrow labels, 01/02/03 numbering, redundant subtitles, captions that explain what is already visible, leaked design notes, decorative badges, status dots, arrows on links, generic link names, filler words, chart clutter and legends a direct label could replace. Applies /pstack:unslop to every string it keeps. With --surface it also fixes gradients and glows, edge accent bars, off-scale spacing, extra-heavy weights and decorative motion. With --plan it shows what it would cut and waits for your OK."
disable-model-invocation: true
argument-hint: "[file, folder or component] [--surface] [--plan]"
allowed-tools: Bash(python3 *scripts/count_tells.py *), Bash(python3 *scripts/load_unslop.py), Read(~/.claude/skills/unslop-ui/**), Read(~/.agents/skills/unslop-ui/**), Read(~/.claude/plugins/cache/**/unslop-ui/**)
---

# Unslop UI

Edit the visible text and decorative chrome of a web page, app screen, chart or dashboard so it stops reading as AI-generated. A good interface is used, not read: keep the words a person needs to act, and cut the rest.

Target: $ARGUMENTS

If the target above is empty or still shows a placeholder, take it from the user's message. With none there either, use the files changed in this conversation, or ask.

Scope: copy, decoration, charts, links and states by default (U1 to U16 and U21 to U23, plus U24 and U25, which are report only). If the arguments include `--surface`, also apply U17 to U20 and U26 (gradients and glows, off-scale spacing, heavy weights, motion, edge accent bars), using the values in [references/tokens.md](references/tokens.md). If they include `--plan`, change nothing: work through the procedure up to the verdict, show the plan and wait for the owner. Strip `--surface` and `--plan` from the target before reading paths.

The rules apply in any language and any script: judge the copy in the language it is written in, by the same tests. The counter never reads words, so it behaves the same on every language: it counts structure (classes, markup, glyphs, chart config). What a string means is your call, not the counter's.

## Writing rules from /pstack:unslop

Apply these to every sentence you keep or write. Cite them as "unslop 13", so they don't read as U rules. They are written with English examples. For copy in another language, apply their intent in that language and skip what only makes sense in English, such as its word lists and idioms.

!`python3 ${CLAUDE_SKILL_DIR}/scripts/load_unslop.py`

If the line above still shows a command instead of rules (agents other than Claude Code), run `python3 scripts/load_unslop.py` from this skill's folder and apply what it prints.

Where these and the UI rules disagree, the UI rules win:

- Labels, buttons, tabs, table headers, KPI captions and badges are fragments by design ("Last 30 days", "+12% vs last month"). The rules about sentences (28, 29) apply to full sentences only: hero copy, descriptions, empty states, errors.
- Rule 13 does not cover a lone "—" that stands for an empty value, or an en dash in a range ("Jan–Mar").

## Cut first, write little

Deleting is the default fix. Where a rule says rewrite (U3, U4, U8, U12, U22, U23), the new text may state only what the source already shows: the product's own copy, the names of its features, the data bound to the screen. Never add a number, a speed, an integration or a benefit you cannot point to in the code. With nothing true to say, delete the string, or leave it and list it as a task. Write a replacement in the language of the string it replaces, with words the screen already uses.

## UI rules

Ids are stable. Cite them as U1 to U26 in the report. The examples are in English. Every rule applies to copy in any language and script: read the example, then judge the same pattern in the language in front of you.

### Interface copy

- **U1. Eyebrow labels.** Small uppercase or letter-spaced text above a heading ("PASSPORT", "FEATURES", "HOW IT WORKS"). It also comes as a pill or chip, often with a dot ("● POLAR EXPEDITIONS"), and as a caption over a menu or dropdown list ("POPULAR DESTINATIONS"). Delete it. The heading already says what the section is.
- **U2. Decorative numbering.** "01 02 03", "01 // Features", "§", "//" prefixes. Delete the numbers, not the text they label. Ask whether someone following the screen would lose their place without them: three feature cards, no; install steps, yes. Keep the numbers when the order is real and the user follows it (steps of a checkout, a numbered install guide, commands to run in order): a list of real steps stays whole, hand-written numbers included: a CSS reset hides the numbers an `<ol>` would draw.
- **U3. Subtitle reflex.** A subtitle under every heading, or a line above the H1. Keep one only when it states a fact the heading doesn't. "Analytics / Understand your data better" loses the second line. The same goes for a blurb under every item of a menu, dropdown or card list ("Greenland / Discover majestic ice fjords"): keep it only when the names alone can't tell the items apart (plan tiers, settings), and then only for the items that need it.
- **U4. Botsplaining.** Captions, helper text and descriptions that narrate what the element visibly does ("Click the button below to get started", "This chart shows revenue over time"). Delete. Empty states, error messages and confirmations of destructive actions are not deleted, but they are edited: one or two plain sentences that say what happened and what to do next, without "Oops!" or an exclamation mark. One that already does that stays exactly as it is. The next step comes from what the code shows (the field, the retry, the setting). With nothing to point to, state the failure plainly and list the missing way out as a task.
- **U5. Leaked design notes.** Text about how the screen works or why it was designed that way, long parentheticals, "(updates in real time)", "(powered by AI)". Delete it. If a user would genuinely look for it, put it inline next to the control it explains, not behind a tooltip or a hover.
- **U6. Status strings.** Facts chained with "·" or "|" ("12 items · Updated 2m ago · Synced · v2.1"). Keep the one fact the user acts on. Put others where they're needed, or drop them. A fact that claims live state ("Synced", "All systems operational") has to pass the real-state test under Decoration, or it goes.
- **U7. Labeling everything.** A label that repeats the placeholder, the icon, the button text or the section heading. Pick one cue. In a form the cue that stays is the visible label: cut a placeholder that repeats it (one that shows a format, "name@company.com", can stay) and helper text that restates it or says what the field is obviously for ("We'll use this email to contact you"). A constraint the user can't guess ("At least 12 characters") stays. A search field with a magnifier icon takes a placeholder or a label, not both.
- **U8. Staccato and empty slogans.** "One. Big. Thing.", "Built different.", "Ship faster. Think less." Rewrite as one sentence that names the thing and what it does, in words the page already uses, or delete.

Length: a section heading, card title or caption inside an app screen stays at 5 words or fewer. A hero heading may be one sentence.

### Decoration

The test for real state, in U6, U9 and U10: the element renders from a condition or a value (`{isLive && ...}`, `status === "online"`, a prop, a query result). Markup that always renders with fixed text is decoration.

- **U9. Badges and pills without real state.** "LIVE", "NEW", "AI", "Beta", "Pro", "🔥 Popular" added for flavor. Keep a badge only if it reflects data the app actually tracks (a real stream is live, an item is actually new since the last visit).
- **U10. Status dots.** Pulsing or colored dots (`animate-pulse`, small `rounded-full` dots) next to text. Keep only if bound to a real live status. A loading skeleton that pulses is not a status dot.
- **U11. Decorative emojis and icons.** In headings, buttons, KPI labels and feature lists, including the icon in a tinted square above each feature card. Delete. An icon stays if it is the control itself (icon button with an `aria-label`), if it carries meaning the text does not, or if it sits in a toolbar or in a menu of actions (edit, copy, delete) where every item has one. A menu of destinations or pages whose icons are generic pictographs (a mountain for Svalbard, a compass for Greenland) is decoration: the icon says nothing the name does not. An icon in a tinted, rounded box is the same tell and goes with its box; delete the wrapper too.

### Charts and dashboards

- **U12. Chart titles that name the chart type.** "Bar chart of monthly revenue" becomes "Monthly revenue". When the data is fixed (a report, a static figure) the title can be the finding instead: "Revenue doubled since March". A chart fed by live data keeps the neutral title, because a finding goes stale.
- **U13. Reading instructions.** Subtitles or captions that explain how to read the chart ("Each bar represents one month", "Hover for details"). Delete.
- **U14. Saying it twice.** Each quantity gets one encoding. A bar, a number on the bar, a gridline at its height and an axis tick all saying the same value is three too many; a KPI with arrow plus percent plus the word "up" plus a sentence under it ("Revenue grew 12% compared to last month") is the same mistake in text. Keep the encoding the reader needs: axis and gridlines for shape, a printed value for the number that matters (often only the last point or the max). A KPI keeps its figure, one direction cue and the period it compares against ("▲ 12% vs last month").
- **U15. Chart scaffolding that competes with the data.** A frame box around the plot area, dark or dense gridlines, minor ticks, thick axis borders, 3D, drop shadows and glows on marks, background fills behind the plot. Delete them, or make what must stay (a few gridlines, one baseline) a hairline in a light gray. Data on top, labels next, scaffolding faintest. Do not redesign the chart: same type, same data, same series colors.
- **U16. Legend where a direct label works.** A legend box that makes the reader match colors to names, when the name could sit at the end of the line or next to the bar. Label the series directly, ideally with its latest value ("This year 1,150"), and remove the legend. Keep a legend for more than four series or when the marks are too close to label.

### Links, actions and states

- **U21. Arrow on links and buttons.** A `→` glyph (`←` in a right-to-left script) or an arrow icon after the text of a link or button ("Learn more →", "Get started" followed by `<ArrowRight />`). Delete it: the text already says where it goes, and a screen reader reads the glyph aloud. An arrow stays when it carries meaning: `↗` on a link that leaves the site, an icon-only Next or Previous button with an `aria-label` (also when the only text beside it is screen-reader-only), a breadcrumb or step separator.
- **U22. One action, one name.** The same action called different things in different places ("Get started", "Start now" and "Begin" all leading to signup), or a button whose result uses another verb ("Publish", then a toast that says "Saved"). Use the name the product already uses most, everywhere. It applies to labels of the same action (signing up, starting a trial). A navigation label and a call to action that point at the same page ("Voyages" in the menu, "Explore voyages" in the hero) do different jobs and keep their own names, and so do two actions with different destinations. Rename only labels in the files you are editing. Names that live elsewhere go in the report as a task.
- **U23. Generic link and button names.** "Click here", "Learn more", "Read more", "Submit": a phrase that carries no information about where it goes or what it does, which a screen reader lists with no context. Replace only these, and their equivalents in other languages, with the destination or the result ("Read the pricing guide", "Save API key"), using only what the code shows: the `href`, the page it opens, the form's purpose. With nothing to go on, leave it and list it as a task. A label that already says what it does ("Begin your journey", "Explore voyages", "Save changes") is not U23, even when it differs from the page title: leave it. One "Learn more" right after its own paragraph is borderline. The same label twice on a page is the tell.
- **U24. Equal stat cards.** A row of identical cards that each hold a big number and a small label, so every figure is equally loud. Report only: name the figure the screen exists to show, and leave the layout to the owner.
- **U25. States nobody handled.** A screen that loads, lists or submits with no loading, empty or error branch in its code: a list that renders nothing for `[]`, a form with nowhere to show an error, a button with no pending state. Report only, never add one. Each missing state is a task that names the component.

### Surface (only with `--surface`)

Each rule pairs the tell with its fix. Read [references/tokens.md](references/tokens.md) for the values. If you can't open it, the values in these rules are enough.

- **U17. Gradients and glows.** A gradient from one hue to another on a surface, button or active item, gradient text (`bg-clip-text`), colored glows (`shadow-[0_0_20px_...]`, `shadow-purple-500/50`), blurred color blobs behind content. Fix: a solid neutral surface, solid text color, a neutral shadow no stronger than `0 1px 2px rgb(0 0 0 / 0.05)`, or a hairline border. A gradient that is only a tone shift inside one neutral can stay.
- **U18. Off-scale spacing.** One-off values such as `mt-[13px]`, `py-[11px]`, `gap: 7px`. Fix: the nearest step of 4, 8, 12, 16, 20, 24, 32, 40, 48, 64. Inside a control, 2, 6, 10 and 14 are also steps. Siblings that do the same job (rows of one list, cards of one row) get the same value. Keep an odd value that exactly centers something.
- **U19. Extra-heavy weights.** `font-extrabold`, `font-black`, `font-weight: 800` or `900`. Fix: 500 or 600, and let size and color carry the hierarchy.
- **U20. Decorative motion.** `transition-all`, `hover:scale-*` on cards, `animate-bounce`, springs and overshoot on simple UI, and a fade or slide entrance on every section as it scrolls into view (`whileInView`, `data-aos`). Fix: transition named properties (`transition-colors`) at 150ms ease-out, keep a press scale of 0.97 to 0.98 if the control has one, and render scroll-revealed content in place. Motion that answers something the user did stays. Pulsing dots are U10.
- **U26. Edge accent bar.** A colored border of 3px or more on the left edge of a card, quote or list item (`border-l-4 border-indigo-500`, `border-left: 4px solid`). Fix: a 1px border all round, or a neutral tint on the selected item. A bar on a real status stays: an alert with `role="alert"`, an error or warning callout.

U17 to U20 and U26 never change the palette, the type family, the type sizes, the radii, the layout structure or the order of sections. They replace a value with a better value, they don't redesign.

For before/after pairs, read [references/examples.md](references/examples.md) when unsure how far to cut.

## Guardrails

- Change visible text and decorative elements only. Do not touch logic, data, colors, spacing tokens or layout structure. The exceptions are chart scaffolding under U15, which may be thinned or lightened, and U17 to U20 and U26 when `--surface` is on.
- U24 and U25 are report only. Never edit a screen for them, and never add a state, a component or a handler.
- Never edit installed skills or agent config: `.claude/`, `.cursor/`, `.agents/`, `.codex/`.
- If the project already has tokens (Tailwind theme, CSS variables, a design-system package), fix toward those and not toward the fallback values in `references/tokens.md`.
- Never change a screen that has nothing to cut. See the verdict in step 3.
- When you delete an element, delete what existed only for it: its now-empty wrapper, a wrapper left holding a single child it only grouped, the margin or gap, the import or variable nothing else uses.
- Never delete a link or a button, whatever its text says. Strip its arrow or decoration, or rename it as U23 says, but it keeps its `href` or handler.
- Never delete `aria-label`, `alt`, `title` on icon buttons, or screen-reader-only text. If cut visible text was the only accessible name, move it into `aria-label`.
- A form field keeps a visible label tied to its input (`for` and `id`, or a wrapping `<label>`). Never swap it for a placeholder or an `aria-label`.
- Text that comes from data, props, i18n files or a CMS: edit it at its source (the translation file, the fixture) or report it, don't hard-code a replacement in the component.
- Claims you cannot verify from the code (customer counts, uptime, ratings, testimonials, customer logos): do not delete or rewrite them. List each as a task.
- If a flagged case earns its place (real state, real order, legal text), keep it and say why in the report.
- Content that looks misplaced or off-topic is a task for the owner, never a deletion. Delete only what a rule names.

## Taste file

If `.unslop-ui/taste.md` exists in the project, read it before step 1. It is the owner's list of what they want gone, and it wins over your own judgment of what is a tell.

- **Bans.** Each bullet under `## Bans` is one more tell, fixed with the same rule as the UI rules: delete first, rewrite only from what the source shows. A ban on a mark or a style (the first three below) changes the mark or the style and keeps the words. Three have a search pattern and a fixed id: exclamation marks (**T1**), uppercase text anywhere, not only eyebrows (**T2**) and middle dots or bullets that stand alone (**T3**, a chain is U6). Any other bullet you find by reading and number T4, T5 in order. Emoji, em dashes and gradients already have U11, unslop 13 and U17, so a ban on them needs no new id.
- **Keep.** Each bullet under `## Keep` names something never to cut or rewrite, such as a badge, a brand name or legal text. List it under "Kept on purpose" when it would have been a hit.
- **Off.** Each bullet under `## Off` names a rule id (`U11`, `unslop 13`, `T1`) to skip entirely, with the reason after it. Do not apply or report that rule; mention the ids once at the top of the report as "Off by taste file".

A taste file never overrides the guardrails above. A ban on uppercase does not delete an `aria-label`, a visible form label or text that renders from real state. With no taste file, T1 to T3 do not run. See [references/taste-example.md](references/taste-example.md) for the format.

## Procedure

Copy this checklist and track it:

```
- [ ] 1. Count: python3 ${CLAUDE_SKILL_DIR}/scripts/count_tells.py [--surface] <target>   (${CLAUDE_SKILL_DIR} is this file's folder; run it from the project root so it finds .unslop-ui/taste.md)
- [ ] 2. Read every visible string and decorative element; tag each problem with U1-U26, a T number from the taste file, or an unslop rule number
- [ ] 3. Verdict: heavy, light or none
- [ ] 4. Edit (with --plan: show the plan and stop; edit only after the owner says go)
- [ ] 5. Count again with the same command
- [ ] 6. Review the result
- [ ] 7. Report
```

**Count.** The counter is a regex heuristic. It finds candidates and gives a before/after number. It counts structure: eyebrow styling, numbering, separators, badge shapes, status dots, emoji, icon tiles, arrow glyphs, the same link text pointing at different places, chart config, em dashes. It cannot see anything that depends on what words mean, in any language: U3, U4, U5, U7, U8, U12, U13, U14, U22, U24, U25, filler words and generic link names. For U11 it counts emojis and Tailwind-style icon tiles, not icons in other markup. With `--surface` it also counts U17 to U20 and U26; it cannot tell a hue-to-hue gradient from a tone shift inside one neutral. It flags legitimate cases too. A count above 0 after editing is fine when every remaining hit is one you kept on purpose. Never delete something legitimate to reach 0. Your reading in step 2 is the real check.

**Verdict**, from the count and your reading:

- **Heavy.** Tells in most of the rules, or the same tell repeated across the screen. Work through every rule that applies, with U24 and U25 as report only.
- **Light.** A few tells. Fix only those. Leave everything else exactly as it is.
- **None.** The counter finds nothing, or only legitimate cases, and reading finds nothing that earns a cut. Say so, edit nothing, and name at most two optional refinements. A clean screen is a result, not a failure.

**Review.** The counter cannot check the reading rules or any guardrail, so read your diff and the edited files once more before reporting:

- Every subtitle, caption, helper text and label still on the screen: does it pass U3, U4, U5 and U7?
- Every string you wrote: is each fact in it in the source, and is it inside the length limit?
- Every deletion: was it tied to real state or a real order (a step list, a badge rendered from a prop)? Put it back if so. Is there an empty wrapper, a wrapper with one child, a leftover margin or an unused import?
- Every input still has its visible label, and every icon button still has a name.
- Read each string you wrote or kept out loud. Where you stumble, shorten it. Where it says nothing new, cut it.
- Nothing outside the scope changed: logic, data, layout, and without `--surface` no styling.

If you can render the screen (a dev server is running, or you have browser tools), look at it: a hole where an element was, or a row with one item left, is a leftover to fix. Fix what you find, then count again.

**Plan (only with `--plan`).** Stop after the verdict and change nothing. Show the table with the Before column only, then one line per planned change (`file:line  U1  delete "INTRODUCING LEDGER"`), each rewrite as old → new, what you would keep on purpose and the tasks. End with one question: apply this plan, or change it? Edit only after the owner answers, and apply the plan exactly as they amended it.

**Report.** Write it in the language the owner used to ask you, and quote screen copy as it is, untranslated. Open with the verdict on a line of its own (`Verdict: none`). Then the table, then up to three lists, and nothing else. When a taste file switches rules off, one line goes above the table: `Off by taste file: U11, unslop 13`. Rows for rules the counter covers use its numbers, the others use your own count from step 2. Kept is how many of the After hits you left on purpose.

| Rule | Before | After | Kept |
|---|---|---|---|
| U1 eyebrow | 6 | 0 | |
| U4 botsplaining | 5 | 0 | |
| U10 status dot | 3 | 1 | 1 |
| unslop 13 em dash | 4 | 0 | |

Skip a list that has nothing in it.

**Rewritten.** Every string you wrote, old and new, with its rule. This is the part the owner has to check. Do not list deletions, the diff shows them.

```
"Finance. Simplified. Finally." → "Manage your team's money" (U8)
```

**Kept on purpose.** One line each, with the reason.

**Tasks.** Anything you found but did not edit (text from a CMS, a claim you cannot verify, a decision that is the owner's), each with its fix:

```
- [ ] src/i18n/en.json:42  U3 subtitle "Understand your data better": remove or replace with a fact
- [ ] src/Keys.tsx  U25 no error state: the key request can fail and nothing is shown
```
