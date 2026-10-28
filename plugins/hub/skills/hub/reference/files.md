# Hub files

```
.local/ai/hub/
├── stack.md                  claim header, projects top-first, history
├── adhoc.md                  queue items that aren't sessions
├── hub.md                    generated view (never hand-edited)
├── sessions/
│   ├── <handle>.md           one per live session
│   └── _done/                archived state files
└── projects/<slug>/          a promoted project's hub, same layout (no projects/ inside)
```

`<handle>` is the workmux handle: the worktree directory name (the lowercased branch, e.g.
`sth-1604-stored-risks`). Templates for every file are in `../templates/`.

## stack.md

```markdown
# Stack

hub_session: <ListAgents name of the session holding the claim>
claimed: <ISO time>

## 1. <Project name>
umbrella: <ticket id and link>
hub: <projects/<slug>/ if promoted, else blank>
Next: <the next 1–3 tickets>
Blocked: <on whom / what, or blank>
Risk: <the one thing most likely to bite, or blank>

## 2. <Project name>
...

## History
- <YYYY-MM-DD> push <Project> at <n>
- <YYYY-MM-DD> move <Project> <from> → <to>
- <YYYY-MM-DD> pop <Project> (<why, if given>)
- <YYYY-MM-DD> claim <session name> (replaced <old name>)
```

Position = the `## <n>.` number; renumber on every push/pop/move. Next/Blocked/Risk are the
user's (or the project hub's) lines; the hub edits them only when the user asks.

## adhoc.md

```markdown
# Ad hoc

- decision: <what the user has to decide or do>
  where: <PR link / ticket / session name / place to do it>
  unblocks: <what moves once it's done, or blank>
  serves: <project name, or blank>
  since: <YYYY-MM-DD>
```

Remove an item when the user says it's done, or when refresh sees its PR merged or closed
(say so in the reply).

## sessions/<handle>.md

```markdown
---
handle: sth-1604-stored-risks
session: sth-1604-stored-risks-48        # ListAgents name; refresh fills it
parent: supply-trace-be-7e               # ListAgents name of the session that dispatched it
branch: STH-1604-stored-risks
ticket: STH-1604
serves: Risk model                       # a stack project, or adhoc
kind: implement                          # implement | review | analysis | rollout | other
state: needs-user                        # see States
needs: sign off on the plan              # one line: the decision, when state is needs-user
pr:                                      # PR URL once opened
after_merge: []                          # every step still owed after the PR merges
handoff: ~/.claude/handoff-prompts/handoff-....md
updated: 2026-10-28T19:40Z
---

## Log
- 2026-10-28 dispatched by hub (queued)
- 2026-10-28 19:40Z plan written; needs sign-off
- 2026-10-28 20:05Z relay from hub: "plan approved, go"
```

### States

| State | Meaning | In the queue? |
|-------|---------|---------------|
| `queued` | dispatched; the worker hasn't reported yet | no |
| `running` | working; nothing needed from the user | no |
| `needs-user` | blocked on the user: `needs` says on what | **yes** |
| `after-merge` | PR merged; `after_merge` steps still open | yes if `needs` is set |
| `done` | nothing left; `after_merge` empty | no |
| `removable` | done and the worktree can go | listed by clean |

### Two writers

- The hub writes the file once at dispatch (`state: queued`, `parent`, `serves`, `kind`,
  `handoff`), fills `session` on refresh, and appends `## Log` lines for relays.
- From its first update on, the worker owns the frontmatter fields `state`, `needs`, `pr`,
  `after_merge` and `updated`. The hub reports disagreements as Drift; it never edits them.

## hub.md (generated)

```markdown
# Hub — refreshed <ISO time> by <hub_session>

## Waiting on you
1. **<decision>** — <where> · unblocks <what> · <project> · since <date>
2. ...

## Stack
### 1. <Project> (<umbrella>)
Now: <derived: sessions serving it and their states, PRs>
Needs you: <derived: count + item numbers above>
Next / Blocked / Risk: <from stack.md>
Sessions:
- <handle> · <kind> · <state> · <PR>
  - <child handle> · <kind> · <state>         (children nest under their parent)

## Ad hoc
- <handle> · <kind> · <state> · <PR>
- <adhoc.md item with no project>

## Drift
- <handle>: <what disagrees, e.g. PR #640 merged but state is running>

## Sources
<which sources were read; any that couldn't be>
```

Order of "Waiting on you": stack position of the item's project (ad hoc last), then oldest
first. Items come from sessions in `needs-user` (and `after-merge` with `needs` set), from
every `adhoc.md` item, and from sessions that stopped without reporting (refresh.md
§ Stopped without reporting), which go after their project's other items.
