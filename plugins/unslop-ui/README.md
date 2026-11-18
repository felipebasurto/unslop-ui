# unslop-ui (Claude Code plugin)

Strips the AI look out of interface and chart copy: eyebrow labels, `01 //` numbering, subtitles that repeat the heading, captions that explain what is visible, badges and status dots wired to nothing. With `--surface` it also fixes gradients, off-scale spacing, extra-heavy weights and decorative motion.

## Install

```
claude plugin marketplace add felipebasurto/unslop-ui
claude plugin install unslop-ui@unslop-ui
```

## Use

```
/unslop-ui:unslop-ui src/pages/landing.tsx
/unslop-ui:unslop-ui src/pages/dashboard.tsx --surface
```

With no argument it works on the files changed in the conversation. It never runs on its own.

This plugin is instructions only: no scripts, no shell commands, and it asks for no tools beyond `Read`, `Grep`, `Glob` and `LS`. It counts tells with the Grep patterns in `skills/unslop-ui/references/finding-tells.md`.

Full documentation, examples and the Codex and Cursor builds, which also ship a counter script: <https://github.com/felipebasurto/unslop-ui>.
