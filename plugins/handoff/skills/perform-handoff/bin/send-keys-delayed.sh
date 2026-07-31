#!/bin/bash
# send-keys-delayed.sh
# Sends keys to a tmux pane after a delay (runs detached)
#
# Usage: send-keys-delayed.sh <delay-seconds> [options] [--] <keys...>
#        send-keys-delayed.sh <delay-seconds> --file <file> [options]
#
# Options:
#   --file <f>  Read keys from file instead of arguments
#   --pane <p>  Target pane (default: $TMUX_PANE)
#   --literal   Use tmux send-keys -l for literal interpretation
#   --          End of options, remaining args are keys
#
# The script exits immediately; the actual send happens in background.
#
# Examples:
#   send-keys-delayed.sh 1 "/clear" Enter        # Sends /clear then Enter after 1s
#   send-keys-delayed.sh 0.5 --literal "hello"   # Sends literal "hello" after 0.5s
#   send-keys-delayed.sh 2 --file prompt.md      # Sends file contents after 2s

set -e

DELAY=""
KEYS=()
KEYS_FILE=""
TARGET_PANE="${TMUX_PANE}"
LITERAL=false

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      KEYS_FILE="$2"
      shift 2
      ;;
    --pane)
      TARGET_PANE="$2"
      shift 2
      ;;
    --literal)
      LITERAL=true
      shift
      ;;
    --)
      shift
      KEYS+=("$@")
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      if [[ -z "$DELAY" ]]; then
        DELAY="$1"
      else
        KEYS+=("$1")
      fi
      shift
      ;;
  esac
done

# Validate
if [[ -z "$DELAY" ]]; then
  echo "Usage: send-keys-delayed.sh <delay-seconds> [options] <keys...>" >&2
  echo "       send-keys-delayed.sh <delay-seconds> --file <file>" >&2
  exit 1
fi

if [[ ${#KEYS[@]} -eq 0 && -z "$KEYS_FILE" ]]; then
  echo "Error: Must provide keys or --file" >&2
  exit 1
fi

if [[ -z "$TARGET_PANE" ]]; then
  echo "Error: No target pane (set TMUX_PANE or use --pane)" >&2
  exit 1
fi

# Spawn detached background process
(
  sleep "$DELAY"
  if [[ -n "$KEYS_FILE" ]]; then
    keys_content="$(cat "$KEYS_FILE")"
    if $LITERAL; then
      tmux send-keys -t "$TARGET_PANE" -l "$keys_content"
    else
      tmux send-keys -t "$TARGET_PANE" "$keys_content"
    fi
  else
    if $LITERAL; then
      tmux send-keys -t "$TARGET_PANE" -l "${KEYS[@]}"
    else
      tmux send-keys -t "$TARGET_PANE" "${KEYS[@]}"
    fi
  fi
) &>/dev/null &
disown

echo "Scheduled: send keys to $TARGET_PANE in ${DELAY}s"
