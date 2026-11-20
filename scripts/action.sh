#!/usr/bin/env bash
# Runs the counter for the GitHub Action in action.yml. Reads INPUT_PATH,
# INPUT_MAX, INPUT_SURFACE and INPUT_TASTE, prints workflow annotations, and
# exits with the counter's status (1 above INPUT_MAX, 2 for a missing path).
set -u

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
args=(--format github)
[ "${INPUT_SURFACE:-false}" = "true" ] && args+=(--surface)
[ -n "${INPUT_MAX:-}" ] && args+=(--max "$INPUT_MAX")
[ -n "${INPUT_TASTE:-}" ] && args+=(--taste "$INPUT_TASTE")
read -r -a paths <<< "${INPUT_PATH:-.}"

output="$(python3 "$root/skills/unslop-ui/scripts/count_tells.py" "${args[@]}" "${paths[@]}")"
status=$?
[ -n "$output" ] && printf '%s\n' "$output"

total="$(printf '%s\n' "$output" | tail -n 1 | sed -nE 's/^unslop-ui: ([0-9]+) possible tells$/\1/p')"
if [ -n "$total" ]; then
  [ -n "${GITHUB_OUTPUT:-}" ] && echo "total=$total" >> "$GITHUB_OUTPUT"
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    limit="${INPUT_MAX:-no limit}"
    printf '### unslop-ui\n\n%s possible tells (limit: %s)\n' "$total" "$limit" >> "$GITHUB_STEP_SUMMARY"
  fi
fi
exit "$status"
