# Learnings — pricing pilot (SWE-2, 14 cells) → skill improvements

Source: `evals/gen/runs/` (meta.json, replies, transcripts), `REVIEW.md`,
`FINDINGS.md`, arena `data.js`. All cells: pricing brief × {html, react} ×
7 configs, agent = devin-subagent (SWE-2).

## What the numbers said

Structural tells (count_tells --surface total → slop 0-100):

| config | html | react |
|---|---|---|
| control | 10 (69 slop) | 6 |
| snippet | 4 | 2 |
| rules | 0 | 0 |
| counter | 0 | 0 |
| full | 2 | 0 |
| edit → unslop | 0 | 1 |
| edit-surface | 1 | 1 |

## Findings

1. **Bug found by the eval**: `count_tells.py` scored the installed skill's own
   example files under `.devin/skills/` — rules/full/edit cells showed 27-38
   phantom tells. Fixed: `.devin`/`.windsurf` added to SKIP_DIRS and the
   runner scores only page sources. *Lesson: the counter must ignore agent
   config dirs; keep SKIP_DIRS in sync with every agent-harness dir.*

2. **The AGENTS.md snippet is the cheapest big win.** ~300 tokens of rules
   before writing removed 60-70% of structural tells in ONE pass, no second
   invocation. Candidates: promote it in README/SKILL.md as the recommended
   quickstart ("prevent tells while writing" vs "clean after").

3. **Zero structural tells ≠ clean.** rules/counter/full hit 0 on the counter
   yet the post-edit passes still found: em dashes, generic/repeated CTA
   names (U22/U23 territory the counter partially sees), decorative eyebrow
   remnants, duplicate badges, unverifiable uptime/discount claims. The
   counter is a floor, never the verdict — keep that framing everywhere.

4. **Post-edit `/unslop-ui` catches what generation misses.** The 4 unslop
   passes produced complete reports (verdict, rule table, rewritten strings,
   kept-on-purpose, tasks) and found semantic issues no config prevented:
   em dashes (unslop 13), CTA naming, glows (U17), multi-value off-scale
   spacing the counter doesn't count.

5. **`--surface` earns its keep.** It caught gradient/glow surfaces and
   spacing issues invisible to the copy pass. Keep it opt-in but documented.

6. **Guardrails held everywhere.** Agents preserved `href="#"` links/buttons,
   kept real state, and reported unverifiable claims ("99.9% uptime") as
   Tasks instead of inventing — in ALL configs including control. The
   skill's "report, don't delete" contract survives contact with agents.

7. **Stack asymmetry**: react cells scored lower at baseline (6 vs 10) —
   component structure produces less raw copy slop. When comparing configs
   across stacks, normalize per-stack or compare within stack.

## Concrete skill-change candidates

- **Counter gaps to close** (each was found by an unslop pass, missed by
  count_tells): em-dash detection beyond current rule, repeated/generic CTA
  label pairs across a page, multi-value off-scale spacing (e.g. `margin: 22px`
  next to `16px`/`24px` scale), glow/box-shadow heuristics for U17.
- **SKILL.md**: add a short "prevent while writing" pointer to
  `references/agents-snippet.md`; consider a writing-mode checklist distilled
  from the snippet for agents that can't install files.
- **Report format held up** — no changes needed there.
- **U24/U25 (missing states)** stayed report-only; the edit passes surfaced
  them correctly as Tasks. Keep.

## What the arena adds next

`github.com/felipebasurto/unslop-arena` grows this to 34 briefs × 2 stacks ×
7 configs (~476 cells) with per-cell telemetry in `factory/ledger.jsonl`,
unslop reports in `factory/reports/`, and human slop guesses vs counter scores
in visitor `localStorage` (export pending a votes endpoint).
