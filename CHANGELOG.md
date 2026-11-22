# Changelog

Versions follow [semantic versioning](https://semver.org). Rule ids keep their meaning and are never reused. Older releases are on the [releases page](https://github.com/felipebasurto/unslop-ui/releases).

## 1.0.0

One skill, instructions only. Paste the repo link to any agent and it works: nothing to install, nothing to run.

- The skill follows the [Agent Skills specification](https://agentskills.io/specification) and passes its validator, so it loads in any agent that supports the standard.
- It can now trigger on its own: the description tells the agent to use it after building or restyling a screen, and when the user asks to clean up interface copy. It no longer needs to be called by name.
- `SKILL.md` stays under the recommended 5,000 tokens. The surface rules and the taste file format moved to `references/`, read only when they apply.

### Removed

- The counter (`count_tells.py`), the pstack loader (`load_unslop.py`), and the counter-based test suite (`evals/incidents/` and `tests/test_skill.py`). The agent's reading was always the real check.
- The plugin's separate copy of the skill (`plugins/unslop-ui/`). The repo root is now the Claude Code plugin, so both paths use the same `SKILL.md`.

### New rules

- **U21** arrows on links and buttons (`Learn more →`). An arrow that is the whole control and `↗` on a link that leaves the site stay.
- **U22** generic link and button names ("Click here", "Learn more", "Submit"), renamed only from what the code shows.
- **U23** equal stat cards: a row of identical big-number cards comes back as a task naming the figure the screen is for. Report only, the layout is never edited.
- **U24** (surface) a colored 3px or thicker bar on the left edge of a card. A bar on a real alert stays.
- **U20** now covers fade-up entrances on scroll (`whileInView`, `data-aos`), numbers that count up on load and charts that redraw from zero on every mount. One hero entrance on a marketing page can stay, and removing an animation also removes its hidden starting state and the code that waits for it.

### Skill

- The writing rules from unslop are inside `SKILL.md`, so one file holds everything.
- The taste file gains an `## Off` section that switches rules off by id, with the reason after the id.
- Surface and plan can be asked for in plain words, not only with `--surface` and `--plan`.
- Works in any language: the agent judges copy in the language it is written in, and reports in the language it was asked in.
- The report opens with the verdict, and the review step reads every kept string out loud.
- The project's files are treated as data, never as instructions to the agent.
- Guardrails from evals: a link or button is never deleted, misplaced content is a task, U2 asks whether the user would lose their place, U4 leaves a good empty state alone, U5 puts help inline instead of in a tooltip.
- U3 now cuts boilerplate reassurance footnotes under CTAs and forms ("No credit card required", "No spam") while keeping subtitles that add real facts; U14 caps KPI cards at one context line and cuts derived restatements of the same figure.

## 0.6.0

- A project taste file, `.unslop-ui/taste.md`, with Bans (T1 exclamation marks, T2 uppercase text, T3 a lone middle dot, and free-text bans the agent reads) and Keep.
- Incident evals: every fixed false positive is a replayable case.
- Issue forms for false positives and missed tells.
