#!/bin/bash
# workmux-handoff.sh
# Hands a handoff doc to a new workmux worktree: creates the worktree and its
# tmux window in the background, with the agent started on the doc.
#
# Usage: workmux-handoff.sh [options] --branch <name> <handoff-file>
#   --branch <name>: Branch for the new worktree (required)
#   --after <cmd>:   What the new agent runs once it has read the doc,
#                    e.g. "/st implement STH-123"
#   --base <ref>:    Base to branch from. Default: origin's default branch,
#                    fetched first; without an origin, workmux's base_branch
#   --dry-run:       Print the workmux command and prompt instead of running
#
# Unlike the new-session target, this needs no marker or SessionStart hook:
# workmux passes the prompt to the agent as an argument, so the doc itself
# is the new agent's first message. The doc stays on disk for recovery.
#
# Prints the new worktree's handle and path.

set -e

BRANCH=""
AFTER=""
BASE=""
DRY_RUN=false
PROMPT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
  --branch)
    BRANCH="$2"
    shift 2
    ;;
  --after)
    AFTER="$2"
    shift 2
    ;;
  --base)
    BASE="$2"
    shift 2
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

if [[ -z "$PROMPT_FILE" || -z "$BRANCH" ]]; then
  echo "Usage: workmux-handoff.sh [options] --branch <name> <handoff-file>" >&2
  exit 1
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Error: handoff document not found: $PROMPT_FILE" >&2
  exit 1
fi
PROMPT_FILE="$(cd "$(dirname "$PROMPT_FILE")" && pwd)/$(basename "$PROMPT_FILE")"

if ! command -v workmux >/dev/null 2>&1; then
  echo "Error: workmux not found on PATH" >&2
  exit 1
fi
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: not in a git repository" >&2
  exit 1
fi

# Branch from a fresh origin default branch, not a possibly stale local main.
FETCH=""
if [[ -z "$BASE" ]] && git remote get-url origin >/dev/null 2>&1; then
  BASE="$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)"
  FETCH="${BASE#origin/}"
fi

# Agent and background invocations can lack a client, so name the session.
SESSION=""
if [[ -n "$TMUX_PANE" ]]; then
  SESSION="$(tmux display-message -p -t "$TMUX_PANE" '#S' 2>/dev/null || true)"
fi

tmp_prompt="$(mktemp "${TMPDIR:-/tmp}/workmux-handoff.XXXXXX")"
trap 'rm -f "$tmp_prompt"' EXIT
{
  printf 'This is a handoff from another session (saved at %s).\n\n' "$PROMPT_FILE"
  cat "$PROMPT_FILE"
  if [[ -n "$AFTER" ]]; then
    printf '\n\n---\n\nOnce you have read this, run `%s`.\n' "$AFTER"
  else
    printf '\n\n---\n\nContinue the work it describes.\n'
  fi
} >"$tmp_prompt"

cmd=(workmux add "$BRANCH" -b -P "$tmp_prompt")
[[ -n "$BASE" ]] && cmd+=(--base "$BASE")
[[ -n "$SESSION" ]] && cmd+=(--parent-session "$SESSION")

if $DRY_RUN; then
  [[ -n "$FETCH" ]] && echo "would run: git fetch origin $FETCH"
  echo "would run: ${cmd[*]}"
  echo "prompt:"
  cat "$tmp_prompt"
  exit 0
fi

[[ -n "$FETCH" ]] && git fetch -q origin "$FETCH"
"${cmd[@]}" >&2

path="$(workmux path "$BRANCH" 2>/dev/null || true)"
if [[ -n "$path" ]]; then
  echo "Worktree created: handle $(basename "$path") at $path"
else
  echo "Worktree created for branch $BRANCH"
fi
