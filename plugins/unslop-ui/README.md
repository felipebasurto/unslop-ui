# unslop-ui (Claude Code plugin)

Strips the AI look out of interface and chart copy: eyebrow labels, `01 //` numbering, subtitles that repeat the heading, captions that explain what is visible, badges and status dots wired to nothing. Also arrows on links, generic link names and filler words. With `--surface` it also fixes gradients, edge accent bars, off-scale spacing, extra-heavy weights and decorative motion. With `--plan` it shows what it would change and waits for your OK.

## Install

```
claude plugin marketplace add felipebasurto/unslop-ui
claude plugin install unslop-ui@unslop-ui
```

## Use

```
/unslop-ui:unslop-ui src/pages/landing.tsx
/unslop-ui:unslop-ui src/pages/dashboard.tsx --surface
/unslop-ui:unslop-ui src/pages/landing.tsx --plan
```

A `.unslop-ui/taste.md` in your project adds your own bans, keeps and switched-off rules. The format is in the [main README](https://github.com/felipebasurto/unslop-ui#your-own-bans-taste-file).

With no argument it works on the files changed in the conversation. It never runs on its own.

This plugin is instructions only: no scripts, no shell commands, and it asks for no tools beyond `Read`, `Grep`, `Glob` and `LS`. It counts tells with the Grep patterns in `skills/unslop-ui/references/finding-tells.md`.

Full documentation, examples and the Codex and Cursor builds, which also ship a counter script, an edit hook and a GitHub Action: <https://github.com/felipebasurto/unslop-ui>.
