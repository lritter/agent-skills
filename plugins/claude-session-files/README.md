# claude-session-files

Records the files Claude writes or edits in a session so a tmux popup picker can
preview them, newest first — handy for pulling up a plan or artifact Claude just
wrote without leaving your layout.

Two halves:

- **The plugin** (this directory) — Claude Code hooks that log touched files per
  session into `/tmp`.
- **The tmux picker** (`tmux/`) — a script + config you copy into your own tmux
  setup. It isn't a plugin component; it lives here as reference copies to install.

## How it works

A `PostToolUse` hook (matching `Edit|Write|MultiEdit|NotebookEdit`) and a
`SessionStart` hook run `bin/record.sh`, which appends touched file paths to a
per-session log under `/tmp` (ephemeral — cleared on reboot) and maintains a
`pane -> session` pointer from the inherited `$TMUX_PANE`:

```
/tmp/claude-session-files-<uid>/sessions/<session_id>.log   # one abs path per line
/tmp/claude-session-files-<uid>/panes/<pane>                # -> session id
```

The hook is silent on stdout and always exits 0, so it never disturbs a session.

The picker resolves the pane you triggered it from to its session, lists that
session's files newest-first (de-duplicated, existing files only) in `fzf` with a
`bat` preview, and opens your choice per an extension → opener table.

## Requirements

- `jq` — for the plugin hook.
- `fzf`, `bat` — for the picker.
- Whatever openers you configure (e.g. `nvim`, [`leaf`](https://leaf.rivolink.mg/),
  and macOS `open`).

## Setup

### 1. Install the plugin

```bash
claude plugin marketplace add lritter/agent-skills   # if not already added
claude plugin marketplace update lritter-agent-skills
claude plugin install claude-session-files@lritter-agent-skills
```

Hooks take effect in **new** Claude Code sessions (they load at process start).

### 2. Install the tmux picker

Copy the two files from this plugin's `tmux/` directory into your tmux config
directory (adjust the source path to wherever you cloned the marketplace):

```bash
cp tmux/claude-file-picker.sh ~/.config/tmux/
cp tmux/claude-openers.conf   ~/.config/tmux/
chmod +x ~/.config/tmux/claude-file-picker.sh
```

Add a binding to your `tmux.conf` (uses whatever your prefix is):

```tmux
# Pick a file Claude wrote/edited this session (newest first), preview + open.
bind C-f display-popup -w 80% -h 80% -E "~/.config/tmux/claude-file-picker.sh"
```

Reload: `tmux source-file ~/.config/tmux/tmux.conf` (or your reload binding).

Now `prefix + C-f` (from the pane running Claude, or any pane in its window) opens
the picker.

> The picker resolves the origin pane itself via `tmux display-message`, because a
> `display-popup` doesn't expand formats in its command arg and runs with
> `$TMUX_PANE` unset — so there's nothing useful to pass on the binding.

## Configuring how files open

`claude-openers.conf` maps a file extension to how the picker opens it:

```
<ext>  <mode>  <command...>
  mode = split -> full-height left tmux pane running:  <command> <file>
         gui   -> launch a non-terminal app detached (no split)
  "*" is the fallback for any unlisted extension.
```

Defaults: `.md` → `leaf`, common code/text → `nvim` (both in a split), images/pdf
→ `open` (detached GUI), everything else → `bat`. Edit the file and re-run the
picker; no tmux reload needed.

## Notes

- The pane → session bridge relies on `$TMUX_PANE` being inherited by the hook,
  which happens when Claude Code runs inside a tmux pane. Outside tmux, the plugin
  still logs per session; only the picker (which is tmux-specific) needs it.
- If you trigger the picker from a side pane (nvim/lazygit/etc.) rather than the
  Claude pane, it falls back to the most-recently-active session among the panes
  in that window.
- Data is under `/tmp` and disappears on reboot by design; there's nothing to
  clean up.
