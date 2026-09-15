#!/usr/bin/env bash
# Record files Claude writes/edits, per session, for the tmux file picker
# (see ~/.config/tmux/claude-file-picker.sh).
#
# Invoked as a Claude Code hook for PostToolUse (Edit|Write|MultiEdit|
# NotebookEdit) and SessionStart. Hook JSON arrives on stdin.
#
# Two hard requirements for a hook:
#   - Print NOTHING to stdout. SessionStart stdout is injected into Claude's
#     context; PostToolUse stdout can surface as tool feedback.
#   - Always exit 0. A nonzero PostToolUse exit shows an error after every
#     edit. So every failure here is swallowed.
#
# Data lives under /tmp (ephemeral; cleared on reboot), keyed by session id,
# with a pane -> session pointer so the tmux picker can resolve it:
#   /tmp/claude-session-files-<uid>/sessions/<session_id>.log   (one path/line)
#   /tmp/claude-session-files-<uid>/panes/<pane>                 (-> session id)

{
  command -v jq >/dev/null 2>&1 || exit 0

  state="/tmp/claude-session-files-$(id -u)"
  mkdir -p "$state/sessions" "$state/panes" 2>/dev/null

  input=$(cat)
  sid=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
  [ -n "$sid" ] || exit 0

  # Refresh the pane -> session pointer so the picker can resolve this pane.
  # $TMUX_PANE is inherited when Claude Code runs inside a tmux pane.
  if [ -n "${TMUX_PANE:-}" ]; then
    printf '%s\n' "$sid" > "$state/panes/${TMUX_PANE#%}" 2>/dev/null
  fi

  log="$state/sessions/$sid.log"
  touch "$log" 2>/dev/null

  event=$(printf '%s' "$input" | jq -r '.hook_event_name // empty' 2>/dev/null)
  if [ "$event" = "PostToolUse" ]; then
    fp=$(printf '%s' "$input" |
      jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null)
    if [ -n "$fp" ]; then
      case "$fp" in
        /*) abs="$fp" ;;
        *)  cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
            abs="${cwd:+$cwd/}$fp" ;;
      esac
      printf '%s\n' "$abs" >> "$log" 2>/dev/null
    fi
  fi
} >/dev/null 2>&1

exit 0
