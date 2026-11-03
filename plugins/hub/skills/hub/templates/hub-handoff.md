## Resume (hub)

Run `/hub resume <this file's path>` in `<repo path>`, or `/hub resume` alone, which finds
this file from the History in `stack.md`. It refreshes, sends each session that's still alive
a relay to resume from its handoff, and opens a fresh agent in each worktree whose session
is gone. The hub state lives in `<hub-dir>/`. Each session's state file is
`sessions/<handle>.md`, and its `handoff:` field names that session's latest handoff.

## Sessions

| Handle | Serves | State | Resume handoff | Answer |
|---|---|---|---|---|
| <handle> | <project, or ad hoc> | <state>: <needs, or the open after_merge steps, short> | <absolute path, or none> | <new / reply only / no reply / not asked> |

Not resumed, because nothing is pending: <handles of done and removable sessions, or none>

## Waiting on you (as of <hub.md refresh time>)

<the numbered list from hub.md, verbatim>

## Relays not sent

- <target session>: <what the relay says>. It waits on <the user's yes, or what else>.

<or "None.">

## Drift

- <line>

<or "None.">

## Key facts

- <what no state file holds: what shipped, tickets filed, workarounds in use, the user's rulings>
