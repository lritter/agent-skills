# handoff-lib.sh — shared by run-handoff.sh and the SessionStart hook.
#
# A pending handoff is a marker file holding two lines: the epoch seconds it
# was written and the absolute path of the handoff doc. The marker is keyed
# so the session that starts next in the same place picks it up:
#   - in tmux: the pane (p<pane id>)
#   - otherwise: the git repo root of the directory, or the directory itself
#     outside a repo (d<hash>). Using the repo root, not the raw directory,
#     keeps the key stable when the working directory moves within a project.

HANDOFF_MARKER_DIR="${HANDOFF_MARKER_DIR:-/tmp/claude-handoff-$(id -u)}"
HANDOFF_MARKER_TTL="${HANDOFF_MARKER_TTL:-600}"

# handoff_marker_key <dir>
handoff_marker_key() {
  if [ -n "${TMUX_PANE:-}" ]; then
    printf 'p%s' "${TMUX_PANE#%}"
    return 0
  fi
  [ -n "${1:-}" ] || return 1
  local root
  root=$(git -C "$1" rev-parse --show-toplevel 2>/dev/null) || root="$1"
  root=$(cd "$root" 2>/dev/null && pwd -P) || return 1
  printf 'd%s' "$(printf '%s' "$root" | shasum | cut -c1-16)"
}

# handoff_marker_path <dir>
handoff_marker_path() {
  local key
  key=$(handoff_marker_key "${1:-}") || return 1
  printf '%s/pending-%s' "$HANDOFF_MARKER_DIR" "$key"
}
