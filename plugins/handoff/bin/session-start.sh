#!/usr/bin/env bash
# SessionStart hook (clear|startup): if a handoff is pending for this pane or
# project (see handoff-lib.sh), tell the new session to read the handoff doc.
#
# Hook JSON arrives on stdin. Stdout is added to the session's context, so
# print nothing unless a handoff is pending, and always exit 0.

(
  . "$(dirname "${BASH_SOURCE[0]}")/handoff-lib.sh"

  input=$(cat)

  # Agent sessions (subagents etc.) must not take the main session's handoff.
  printf '%s' "$input" | grep -Eq '"agent_type"[[:space:]]*:[[:space:]]*"[^"]' && exit 0

  dir=""
  if [ -z "${TMUX_PANE:-}" ]; then
    command -v jq >/dev/null 2>&1 &&
      dir=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
    dir="${dir:-${CLAUDE_PROJECT_DIR:-$PWD}}"
  fi

  marker=$(handoff_marker_path "$dir") || exit 0
  [ -f "$marker" ] || exit 0

  # Claim it: only one session can win the rename.
  claimed="$marker.claimed.$$"
  mv "$marker" "$claimed" || exit 0
  { read -r written; read -r doc; } <"$claimed"
  rm -f "$claimed"

  case "$written" in '' | *[!0-9]*) exit 0 ;; esac
  [ $(($(date +%s) - written)) -le "$HANDOFF_MARKER_TTL" ] || exit 0
  [ -f "$doc" ] || exit 0

  printf 'A handoff from a previous session is pending. Read %s and continue the work it describes before doing anything else.\n' "$doc"
) 2>/dev/null

exit 0
