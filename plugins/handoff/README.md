# handoff

Write a handoff document capturing session state, then apply it — return the
contents, dispatch a subagent, start a fresh session, or start an agent in a
new workmux worktree.

- `create-handoff` writes the doc to `~/.claude/handoff-prompts/`.
- `perform-handoff` applies it.
- `work-on` (`/handoff:work-on <what>`) names a branch, writes a handoff for
  the work, and applies it to a new workmux worktree.

## How a new-session handoff works

The handoff is never typed into the terminal (long typed input gets
truncated). Instead:

1. `run-handoff.sh` writes a small marker to `/tmp/claude-handoff-<uid>/`
   naming the doc. The marker is keyed to the tmux pane, or outside tmux to
   the project's git root.
2. In tmux it sends `/clear`, then `continue`. Outside tmux, you run `/clear`
   (or restart `claude`) and send any message yourself.
3. The plugin's `SessionStart` hook (`bin/session-start.sh`, on `clear` and
   `startup`) finds the marker, deletes it, and adds "Read <doc> and continue"
   to the new session's context.

The hook prints nothing and exits immediately when no handoff is pending,
and ignores agent sessions so a subagent can't take your handoff.

Retention:

- Markers expire after 10 minutes (`HANDOFF_MARKER_TTL`, seconds).
- Handoff docs are kept 7 days (`HANDOFF_RETAIN_DAYS`) so a failed handoff
  can be retried, and pruned on each handoff.

## How a workmux handoff works

`workmux-handoff.sh` fetches origin's default branch and runs
`workmux add <branch> -b -P <prompt> --base origin/<default>`, with
`--parent-session` set to the caller's tmux session. workmux passes the prompt
to the new agent as an argument, so the doc itself (plus an optional
follow-up command such as `/st implement STH-123`) is the agent's first
message: no marker or hook. The caller's session keeps going.

## Tests

```
plugins/handoff/tests/test.sh
```

Uses a scratch home, marker dir, and a fake `tmux`; never sends keys to a
real pane.
