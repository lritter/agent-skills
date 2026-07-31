#!/bin/bash
# run-handoff.sh
# Sends a handoff prompt to the current tmux pane
#
# Usage: run-handoff.sh [options] [prompt-file]
#   --clear:              Send /clear before the prompt
#   --keep:               Don't delete the prompt file after sending
#   --delay <sec>:        Schedule send after delay (exits immediately, runs in background)
#   --escape-delay <sec>: Delay after Escape before /clear (default: 0.3)
#   --clear-delay <sec>:  Delay after /clear processes before prompt (default: 6.0)
#   --prompt-delay <sec>: Delay after prompt before Enter (default: 0.3)
#   --no-auto-send:       Don't send Enter after prompt (leave in buffer for review)
#   prompt-file:          Path to prompt file (default: ~/.claude/handoff-prompts/pane-<id>.md)
#
# Typically called after exiting Claude, or from a hook.
# Use --delay when calling from within Claude so it can return to input loop.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDOFF_DIR="$HOME/.claude/handoff-prompts"
DO_CLEAR=false
DELETE_FILE=true
DELAY=""
ESCAPE_DELAY="0.3"
CLEAR_DELAY="4.0"
PROMPT_DELAY="0.3"
AUTO_SEND=true
PROMPT_FILE=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  --clear)
    DO_CLEAR=true
    shift
    ;;
  --keep)
    DELETE_FILE=false
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

# If no file specified, use session/window/pane-based default
if [[ -z "$PROMPT_FILE" ]]; then
  if [[ -z "$TMUX_PANE" ]]; then
    echo "Error: No prompt file specified and not running in tmux" >&2
    exit 1
  fi
  # Get session, window, and pane IDs for fully unique naming
  session_name=$(tmux display-message -p '#{session_name}')
  window_id=$(tmux display-message -p '#{window_id}')
  window_id="${window_id#@}"
  pane_id="${TMUX_PANE#%}"
  PROMPT_FILE="$HANDOFF_DIR/s${session_name}-w${window_id}-p${pane_id}.md"
fi

# Check for handoff file
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "No handoff prompt found: $PROMPT_FILE"
  exit 0
fi

# Require tmux for send-keys
if [[ -z "$TMUX_PANE" ]]; then
  echo "Error: Not running in tmux (TMUX_PANE not set)" >&2
  exit 1
fi

prompt="$(cat "$PROMPT_FILE")"

# If --delay specified, use send-keys-delayed.sh and exit immediately
if [[ -n "$DELAY" ]]; then
  # Write prompt to temp file for delayed send (don't delete original yet)
  TEMP_PROMPT=$(mktemp)
  cat "$PROMPT_FILE" >"$TEMP_PROMPT"

  if $DO_CLEAR; then
    # Based on working Windows script - need careful sequencing:
    # 1. Escape to clear pending input
    # 2. Type /clear
    # 3. Enter (separate, with delay)
    # 4. Wait for /clear to fully process (~5-8s)
    # 5. Send prompt
    # 6. Enter to submit

    T1=$(echo "$DELAY" | bc)
    "$SCRIPT_DIR/send-keys-delayed.sh" "$T1" Escape

    T2=$(echo "$T1 + $ESCAPE_DELAY" | bc)
    "$SCRIPT_DIR/send-keys-delayed.sh" "$T2" --literal "/clear"

    T3=$(echo "$T2 + $ESCAPE_DELAY" | bc)
    "$SCRIPT_DIR/send-keys-delayed.sh" "$T3" Enter

    # Wait for /clear to fully process
    T4=$(echo "$T3 + $CLEAR_DELAY" | bc)
    "$SCRIPT_DIR/send-keys-delayed.sh" "$T4" --literal --file "$TEMP_PROMPT"

    if $AUTO_SEND; then
      T5=$(echo "$T4 + $PROMPT_DELAY" | bc)
      "$SCRIPT_DIR/send-keys-delayed.sh" "$T5" Enter
    fi
  else
    "$SCRIPT_DIR/send-keys-delayed.sh" "$DELAY" --literal --file "$TEMP_PROMPT"
    if $AUTO_SEND; then
      # Schedule Enter to submit the prompt
      T2=$(echo "$DELAY + $PROMPT_DELAY" | bc)
      "$SCRIPT_DIR/send-keys-delayed.sh" "$T2" Enter
    fi
  fi

  # Clean up original file (temp file cleaned up by delayed script? no, we need to handle that)
  # Actually, keep temp file since background process needs it. It's in /tmp so will be cleaned eventually.
  if $DELETE_FILE; then
    rm "$PROMPT_FILE"
  fi

  if $AUTO_SEND; then
    echo "Handoff scheduled in ${DELAY}s (auto-send)"
  else
    echo "Handoff scheduled in ${DELAY}s (review in buffer)"
  fi
  exit 0
fi

# Immediate mode (no delay)
prompt="$(cat "$PROMPT_FILE")"

# Clean up the file (unless --keep)
if $DELETE_FILE; then
  rm "$PROMPT_FILE"
fi

if $DO_CLEAR; then
  # Send /clear command
  tmux send-keys "/clear" Enter
  sleep "$CLEAR_DELAY"
fi

# Send the prompt
# Using send-keys with literal flag to handle special characters
tmux send-keys -l "$prompt"

echo "Handoff prompt sent (from $PROMPT_FILE)"
