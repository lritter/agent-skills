#!/usr/bin/env bash
# Tests for the handoff marker flow: run-handoff.sh writes a marker,
# session-start.sh (the SessionStart hook) consumes it.
#
# Usage: plugins/handoff/tests/test.sh
# Uses a scratch HOME and marker dir; never sends keys to tmux.

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$ROOT/bin/session-start.sh"
RUN="$ROOT/skills/perform-handoff/bin/run-handoff.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Fake tmux first on PATH: record calls, never touch a real tmux server.
# Also unset TMUX so nothing can find the real server by accident.
mkdir -p "$TMP/fakebin"
cat >"$TMP/fakebin/tmux" <<'FAKE'
#!/bin/sh
echo "$*" >>"$TMUX_LOG"
FAKE
chmod +x "$TMP/fakebin/tmux"
export PATH="$TMP/fakebin:$PATH" TMUX_LOG="$TMP/tmux.log"
unset TMUX
export HOME="$TMP/home"
export HANDOFF_MARKER_DIR="$TMP/markers"
mkdir -p "$HOME/.claude/handoff-prompts" "$TMP/repo/sub"
git -C "$TMP/repo" init -q

DOC="$HOME/.claude/handoff-prompts/handoff-1-abcd.md"
echo "# handoff" >"$DOC"

fails=0
pass() { echo "ok   $1"; }
fail() { echo "FAIL $1${2:+: $2}"; fails=$((fails + 1)); }

markers() { ls "$HANDOFF_MARKER_DIR" 2>/dev/null | wc -l | tr -d ' '; }
reset() { rm -rf "$HANDOFF_MARKER_DIR"; }

# hook <json> -> stdout of the hook, with a pane set unless PANE is empty
hook() { printf '%s' "$1" | TMUX_PANE="${PANE-%7}" "$HOOK"; }

# queue [args...] -> run-handoff.sh from a repo subdir; PANE sets TMUX_PANE
# (keys go to the fake tmux)
queue() { (cd "$TMP/repo/sub" && TMUX_PANE="${PANE-}" "$RUN" "$@"); }

# --- hook with no marker -------------------------------------------------
reset
out=$(hook '{"source":"clear","cwd":"/nowhere"}'); rc=$?
[[ -z "$out" && $rc -eq 0 ]] && pass "no marker: silent, exit 0" || fail "no marker" "rc=$rc out=$out"

# --- pane-keyed round trip -----------------------------------------------
reset
PANE=%7 queue "$DOC" >/dev/null
[[ $(markers) == 1 ]] && pass "run-handoff writes one marker" || fail "marker written" "count=$(markers)"
out=$(hook '{"source":"clear","cwd":"/nowhere"}')
[[ "$out" == *"$DOC"* ]] && pass "hook prints doc path" || fail "hook prints doc path" "$out"
[[ $(markers) == 0 ]] && pass "hook consumes marker" || fail "hook consumes marker" "count=$(markers)"
out=$(hook '{"source":"clear","cwd":"/nowhere"}')
[[ -z "$out" ]] && pass "second session gets nothing" || fail "second session" "$out"

# --- other pane doesn't take it ------------------------------------------
reset
PANE=%7 queue "$DOC" >/dev/null
out=$(PANE=%8 hook '{"source":"clear","cwd":"/nowhere"}')
[[ -z "$out" && $(markers) == 1 ]] && pass "other pane ignored" || fail "other pane ignored" "$out"

# --- agent sessions don't take it ----------------------------------------
reset
PANE=%7 queue "$DOC" >/dev/null
out=$(hook '{"source":"startup","cwd":"/nowhere","agent_type":"general-purpose"}')
[[ -z "$out" && $(markers) == 1 ]] && pass "agent session ignored, marker kept" || fail "agent session" "$out"

# --- stale marker --------------------------------------------------------
reset
PANE=%7 queue "$DOC" >/dev/null
out=$(HANDOFF_MARKER_TTL=-1 hook '{"source":"clear","cwd":"/nowhere"}')
[[ -z "$out" ]] && pass "stale marker ignored" || fail "stale marker" "$out"

# --- marker whose doc is gone --------------------------------------------
reset
cp "$DOC" "$DOC.bak"
PANE=%7 queue "$DOC" >/dev/null
rm "$DOC"
out=$(hook '{"source":"clear","cwd":"/nowhere"}')
mv "$DOC.bak" "$DOC"
[[ -z "$out" ]] && pass "missing doc ignored" || fail "missing doc" "$out"

# --- no tmux: keyed by repo root, from a different subdirectory ----------
reset
out=$(PANE= queue "$DOC")
[[ "$out" == *"/clear"* ]] && pass "no tmux: tells user to /clear" || fail "no tmux message" "$out"
out=$(PANE= hook "{\"source\":\"clear\",\"cwd\":\"$TMP/repo\"}")
[[ "$out" == *"$DOC"* ]] && pass "no tmux: repo-root key matches across subdirs" || fail "repo-root key" "$out"

# --- no tmux: different repo doesn't take it -----------------------------
reset
mkdir -p "$TMP/other" && git -C "$TMP/other" init -q
PANE= queue "$DOC" >/dev/null
out=$(PANE= hook "{\"source\":\"clear\",\"cwd\":\"$TMP/other\"}")
[[ -z "$out" ]] && pass "no tmux: other repo ignored" || fail "other repo" "$out"

# --- tmux path works without jq ------------------------------------------
reset
PANE=%7 queue "$DOC" >/dev/null
nojq="$TMP/nojq"; mkdir -p "$nojq"
for t in tmux bash cat date rm mv mkdir printf grep git shasum cut id dirname basename; do
  p=$(command -v "$t") && ln -sf "$p" "$nojq/$t"
done
out=$(printf '%s' '{"source":"clear"}' | TMUX_PANE=%7 PATH="$nojq" "$HOOK")
PATH="$nojq" command -v jq >/dev/null && fail "jq-free PATH still has jq"
[[ "$out" == *"$DOC"* ]] && pass "tmux path works without jq" || fail "without jq" "$out"

# --- tmux mode sends /clear and "continue" to the pane, nothing else ----
reset; : >"$TMUX_LOG"
PANE=%7 queue --clear --clear-delay 0 --prompt-delay 0 "$DOC" >/dev/null
log=$(cat "$TMUX_LOG")
[[ "$log" == *"-t %7"*"/clear"* && "$log" == *"-t %7 -l continue"* && "$log" != *"$DOC"* ]] &&
  pass "tmux mode: /clear + continue to the pane, no doc text" || fail "tmux keys" "$log"
grep -v -- "-t %7" "$TMUX_LOG" | grep -q . && fail "tmux call without -t %7" "$log" || pass "every tmux call targets the pane"

# --- run-handoff argument handling ---------------------------------------
reset
out=$(PANE= queue 2>&1); rc=$?
[[ $rc -ne 0 ]] && pass "run-handoff requires a doc path" || fail "requires doc path" "rc=$rc"
out=$(PANE=%7 queue --clear --dry-run "$DOC")
[[ "$out" == *"/clear"* && "$out" == *"continue"* && $(markers) == 0 ]] &&
  pass "dry-run prints keys, writes nothing" || fail "dry-run" "$out"

# --- run-handoff prunes old docs, keeps the one it sends -----------------
reset
old="$HOME/.claude/handoff-prompts/handoff-0-old.md"
echo old >"$old"
touch -t 202001010000 "$old" "$DOC"
PANE=%7 queue "$DOC" >/dev/null
[[ ! -e "$old" && -e "$DOC" ]] && pass "prunes old docs, keeps current" || fail "prune"

echo
[[ $fails -eq 0 ]] && echo "all passed" || { echo "$fails failed"; exit 1; }
