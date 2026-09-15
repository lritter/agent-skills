# claude-session-files

Records the files Claude writes or edits in a session so a tmux popup picker can
preview them, newest first — handy for pulling up a plan or artifact Claude just
wrote without leaving your layout.

## How it works

A `PostToolUse` hook (matching `Edit|Write|MultiEdit|NotebookEdit`) and a
`SessionStart` hook run `bin/record.sh`, which appends touched file paths to a
per-session log under `/tmp` (ephemeral) and maintains a `pane -> session`
pointer using the inherited `$TMUX_PANE`:

```
/tmp/claude-session-files-<uid>/sessions/<session_id>.log   # one abs path per line
/tmp/claude-session-files-<uid>/panes/<pane>                # -> session id
```

The hook is silent and always exits 0, so it never interferes with a session.

## The tmux side (not in this repo)

The picker lives with your tmux config, since it's tmux-specific:

- `~/.config/tmux/claude-file-picker.sh` — resolves the triggering pane to its
  session, lists files newest-first (deduped, existing only) in `fzf` with a
  `bat` preview, and opens the choice per an openers table.
- `~/.config/tmux/claude-openers.conf` — maps extensions to how they open
  (terminal apps in a full-height left split; GUI apps detached).

Binding (prefix is `C-Space`):

```tmux
bind C-f display-popup -w 80% -h 80% -E \
  "~/.config/tmux/claude-file-picker.sh '#{pane_id}'"
```

`#{pane_id}` passes the *origin* pane, since inside the popup `$TMUX_PANE` is the
popup's own pane.

## Install

Enable from the marketplace (hooks load on the next Claude Code session):

```bash
claude plugin marketplace update lritter-agent-skills
claude plugin install claude-session-files@lritter-agent-skills
```

Requires `jq`. The tmux side additionally uses `fzf` and `bat`.
