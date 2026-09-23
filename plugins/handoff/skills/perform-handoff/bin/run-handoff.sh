#!/bin/bash
# run-handoff.sh
# Queues a handoff doc for the next session in this tmux pane (or project),
# and in tmux, starts that session.
#
# Usage: run-handoff.sh [options] <handoff-file>
#   --clear:              Send /clear, then "continue", to the pane (tmux only)
#   --delay <sec>:        Schedule sends after delay (exits immediately, runs in background)
#   --escape-delay <sec>: Delay after Escape before /clear (default: 0.3)
#   --clear-delay <sec>:  Delay after /clear processes before "continue" (default: 4.0)
#   --prompt-delay <sec>: Delay after "continue" before Enter (default: 0.3)
#   --no-auto-send:       Don't send Enter after "continue" (leave in buffer)
#   --dry-run:            Print the marker and keys instead of writing/sending
#
# The handoff itself is never typed into the pane: long send-keys input gets
# truncated. Instead this writes a marker (see bin/handoff-lib.sh) that the
# plugin's SessionStart hook picks up when the next session starts, and adds
# the doc's path to that session's context. The only keys sent are /clear and
# "continue", to start the turn; losing some of them is harmless.
#
# Outside tmux, the marker is written and the user runs /clear themselves.
#
# The doc is kept so a failed handoff can be recovered. Handoff docs in
# ~/.claude/handoff-prompts older than $HANDOFF_RETAIN_DAYS days (default: 7)
# are pruned on each run.
#
# Use --delay when calling from within Claude so it can return to input loop.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/../../../bin/handoff-lib.sh"

HANDOFF_DIR="$HOME/.claude/handoff-prompts"
RETAIN_DAYS="${HANDOFF_RETAIN_DAYS:-7}"
KICK="continue"
DO_CLEAR=false
DELAY=""
ESCAPE_DELAY="0.3"
CLEAR_DELAY="4.0"
PROMPT_DELAY="0.3"
AUTO_SEND=true
DRY_RUN=false
PROMPT_FILE=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  --clear)
    DO_CLEAR=true
    shift
    ;;
  --delay)
    DELAY="$2"
    shift 2
    ;;
  --escape-delay)
    ESCAPE_DELAY="$2"
    shift 2
    ;;
  --clear-delay)
    CLEAR_DELAY="$2"
    shift 2
    ;;
  --prompt-delay)
    PROMPT_DELAY="$2"
    shift 2
    ;;
  --no-auto-send)
    AUTO_SEND=false
    shift
    ;;
  --dry-run)
    DRY_RUN=true
    shift
    ;;
  -*)
    echo "Unknown option: $1" >&2
    exit 1
    ;;
  *)
    PROMPT_FILE="$1"
    shift
    ;;
  esac
done

if [[ -z "$PROMPT_FILE" ]]; then
  echo "Usage: run-handoff.sh [options] <handoff-file>" >&2
  exit 1
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Error: handoff document not found: $PROMPT_FILE" >&2
  exit 1
fi
PROMPT_FILE="$(cd "$(dirname "$PROMPT_FILE")" && pwd)/$(basename "$PROMPT_FILE")"

MARKER="$(handoff_marker_path "$PWD")"

if $DRY_RUN; then
  echo "would write marker: $MARKER -> $PROMPT_FILE"
  if [[ -n "$TMUX_PANE" ]] && $DO_CLEAR; then
    echo "would send to $TMUX_PANE: /clear, $KICK"
    $AUTO_SEND && echo "would send to $TMUX_PANE: Enter"
  fi
  exit 0
fi

# Prune old handoff docs (never the one being handed off) and stale markers
if [[ -d "$HANDOFF_DIR" ]]; then
  find "$HANDOFF_DIR" -maxdepth 1 -type f -name '*.md' -mtime +"$RETAIN_DAYS" \
    ! -path "$PROMPT_FILE" -delete 2>/dev/null || true
fi
if [[ -d "$HANDOFF_MARKER_DIR" ]]; then
  find "$HANDOFF_MARKER_DIR" -maxdepth 1 -type f -name 'pending-*' \
    -mmin +$(((HANDOFF_MARKER_TTL + 59) / 60)) -delete 2>/dev/null || true
fi

# Write the marker atomically so the hook never reads a partial one
mkdir -p "$HANDOFF_MARKER_DIR"
chmod 700 "$HANDOFF_MARKER_DIR"
tmp_marker="$(mktemp "$HANDOFF_MARKER_DIR/.tmp.XXXXXX")"
printf '%s\n%s\n' "$(date +%s)" "$PROMPT_FILE" >"$tmp_marker"
mv "$tmp_marker" "$MARKER"

if [[ -z "$TMUX_PANE" ]]; then
  echo "Handoff queued (not in tmux). Run /clear, then send any message."
  exit 0
fi

if ! $DO_CLEAR; then
  echo "Handoff queued for pane $TMUX_PANE. The next /clear there will pick it up."
  exit 0
fi

# If --delay specified, use send-keys-delayed.sh and exit immediately
if [[ -n "$DELAY" ]]; then
  # Careful sequencing:
  # 1. Escape to clear pending input
  # 2. Type /clear
  # 3. Enter (separate, with delay)
  # 4. Wait for /clear to fully process (the hook runs here)
  # 5. Type "continue"
  # 6. Enter to submit
  T=$(echo "$DELAY" | bc)
  "$SCRIPT_DIR/send-keys-delayed.sh" "$T" Escape

  T=$(echo "$T + $ESCAPE_DELAY" | bc)
  "$SCRIPT_DIR/send-keys-delayed.sh" "$T" --literal "/clear"

  T=$(echo "$T + $ESCAPE_DELAY" | bc)
  "$SCRIPT_DIR/send-keys-delayed.sh" "$T" Enter

  T=$(echo "$T + $CLEAR_DELAY" | bc)
  "$SCRIPT_DIR/send-keys-delayed.sh" "$T" --literal "$KICK"

  if $AUTO_SEND; then
    T=$(echo "$T + $PROMPT_DELAY" | bc)
    "$SCRIPT_DIR/send-keys-delayed.sh" "$T" Enter
    echo "Handoff scheduled in ${DELAY}s (auto-send)"
  else
    echo "Handoff scheduled in ${DELAY}s (review in buffer)"
  fi
  exit 0
fi

# Immediate mode (no delay)
tmux send-keys -t "$TMUX_PANE" "/clear" Enter
sleep "$CLEAR_DELAY"
tmux send-keys -t "$TMUX_PANE" -l "$KICK"
if $AUTO_SEND; then
  sleep "$PROMPT_DELAY"
  tmux send-keys -t "$TMUX_PANE" Enter
fi

echo "Handoff sent (pointing at $PROMPT_FILE)"
