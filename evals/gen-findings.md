# Findings

Patterns from REVIEW.md verdicts, each one a candidate change to
`skills/unslop-ui/`. Format: what the runs showed → what to try → result.

## Pilot 1 — pricing × {html, react} × devin-subagent (SWE-2) × 7 configs

14 runs, `runs/_batches/pilot1.json`. Counter totals (structure only —
meaning-level tells are invisible to it, human review is the real signal):

| config | html tells (surface) | react tells (surface) | gen secs |
|---|---|---|---|
| control | 10 (27) | 6 (13) | ~550-620 |
| snippet | 4 (6) | 2 (3) | ~460-630 |
| rules | 0 (0) | 0 (0) | ~530-600 |
| counter | 0 (0) | 0 (0) | ~570-620 |
| full | 2 (2) | 0 (0) | ~520-640 |
| edit → unslop | 0 (1) | 1 (6) | +~400 |
| edit-surface → unslop --surface | 1 (3)* | 1 (5) | +~400-480 |

*edit-surface-html still finishing at time of writing.

### Bugs the pilot already caught

- **Counter scored the skill itself.** With the skill installed under
  `.devin/skills/`, `count_tells.py .` counted `examples.md`/`SKILL.md`
  (full of slop examples) as page tells: rules=27, full=38 phantom hits.
  Fixed twice: `SKILL_DIRS` now skips `.devin`/`.windsurf`, and the runner
  scores only page targets (`index.html`+`styles.css` or `src/`). The
  edit-surface-react subagent noticed the same thing independently.
- **`count_tells.py` self-matches.** In the `counter` config the script sits
  in `work/scripts/` and its own patterns score ~9 hits. Not fixed yet —
  candidate: skip own file, or accept and document.

### Early observations (pending human review)

- `snippet` (AGENTS.md rules, ~300 tokens) already removes ~60-70% of
  structural tells vs control at zero extra passes. Cheapest win so far.
- `rules` and `counter` hit 0 on this brief — but "0 tells" ≠ "reads human":
  several runs report near-identical competent-but-bland output; the
  differentiator may be in meaning-level tells (U3/U4/U8) the counter can't
  see. REVIEW.md verdicts decide.
- `full` ≈ `rules` on tells but the agent also ran the counter itself and
  cited AGENTS.md — the combination seems to change *behavior*, not just
  output. Worth a look at replies.
- The `edit` pass reliably produces the skill's report format (verdict
  table, Rewritten, Kept on purpose, Tasks) and catches things generation
  missed (em dashes, U22 naming, U17 glow). Costs a second full pass.
- `edit-surface` spent real effort on U18 multi-value shorthands the counter
  can't see — surface pass earns its keep on visual tells.
- All agents left `href="#"` placeholders and unverifiable claims ("99.9%
  uptime SLA", "50% off for startups") — correctly reported as Tasks, never
  invented over. Guardrails hold across configs.

### Telemetry notes for the video

- gen pass: ~460-640s per cell (subagent wall clock, includes tool use).
- unslop pass: ~400-480s — roughly +70% time over generation alone.
- Token usage: subagent path doesn't export ATIF; `meta.tokens` is empty.
  The `devin-cli` agent (`devin -p --export`) captures it once authed.
