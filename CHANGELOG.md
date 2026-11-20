# Changelog

Versions follow [semantic versioning](https://semver.org). What counts as breaking is listed under [Versioning](README.md#versioning). Older releases are on the [releases page](https://github.com/felipebasurto/unslop-ui/releases).

## 1.0.0

The rule set, the counter output and the taste file format are now stable.

### New rules

- **U21** arrows on links and buttons (`Learn more →`, an arrow icon after the text). An arrow that is the whole control, one beside screen-reader-only text, and `↗` on a link that leaves the site stay.
- **U22** one action, one name: the product's most used name everywhere.
- **U23** generic link and button names ("Click here", "Learn more", "Submit"), renamed only from what the code shows.
- **U24** equal stat cards and **U25** states nobody handled (no empty, loading or error branch). Both are report only: they come back as tasks and the screen is never edited for them.
- **U26** (with `--surface`) a colored 3px or thicker border on the left edge of a card. A bar on a real alert stays.
- **U20** now also covers fade-up entrances on scroll (`whileInView`, `data-aos`), and says to render that content in place.
- Existing rules sharpened: U4 takes its next step only from what the code shows, and U5 puts help inline instead of in a tooltip.

### Skill

- `--plan` shows the verdict, every cut and every rewrite, and waits for the owner before editing.
- The rules apply in any language. The counter's patterns cover English and Spanish (U9, U12, U13, U23, filler vocabulary).
- The review step reads every kept string out loud, and Tasks lists the states the code never handles.
- The taste file gains an `## Off` section that switches rules off by id, with the reason after the id.

### Counter

- Counts filler vocabulary (`unslop 7 AI vocabulary`: "seamless", "robust", "empower", and their Spanish equivalents) in text and strings, never in identifiers, class names, tests or specs.
- `--format github` prints workflow annotations, with paths escaped.
- Agent config folders (`.claude`, `.cursor`, `.agents`, `.codex`) are not scanned.
- Backticked numbers in Markdown are code, not numbering.

### Around the skill

- An opt-in edit hook for Claude Code and Cursor ([`scripts/hook.py`](skills/unslop-ui/scripts/hook.py)) that tells the agent what a file it just wrote contains. It never edits or blocks and fails open.
- A GitHub Action (`felipebasurto/unslop-ui@v1`) that annotates, summarizes and fails above a limit.
- A short block for `AGENTS.md` that keeps the tells out while the agent writes.

### Evals

- Six new fixtures (`links`, `states`, `plan`, `es`, `surface-new`, `taste`), and fixtures can set `args` and `report_regex`.
- `evals/run.py` installs this checkout's skill into each fixture copy, so a run tests the working tree and not an installed copy.
- 22 incident cases replay with `evals/run.py --incidents`, and an expectation that names a rule the run does not count now fails.

## 0.6.0

- A project taste file, `.unslop-ui/taste.md`, with Bans (T1 exclamation marks, T2 uppercase text, T3 a lone middle dot, and free-text bans the agent reads) and Keep.
- Incident evals: every fixed false positive is a replayable case.
- Issue forms for false positives and missed tells.
