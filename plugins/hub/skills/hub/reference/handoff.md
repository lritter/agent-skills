# Handoff and resume

`handoff` makes the whole hub resumable after a `/clear` or a restart. Every session with
pending work writes its own handoff, and the hub writes one that points at all of them.
`resume` takes a hub handoff and gets each of those sessions going again.

## Handoff

`handoff [--project <slug>]`

This command spans turns. The hub sends its requests and ends its turn, and the answers
arrive later as replies and idle notices.

1. **Refresh**, following refresh.md, without the reply.
2. **Who to ask.** Every session whose state is `queued`, `running`, `needs-user` or
   `after-merge`. Skip `done` and `removable`. A `done` session that still lists steps in
   `after_merge` isn't asked either; it goes in the hub handoff's Drift.
3. **Ask.** Running `/hub handoff` is the user's yes for this request, so send it without
   asking again. Send it to each session with SendMessage and `notify_when_idle: true`:

   ```
   From the hub: the user wants a resume handoff from every session with pending work, so each one can be resumed fresh.
   1. Bring your state file up to date: <hub-dir>/sessions/<handle>.md. Leave `state` as it is; writing a handoff isn't a stop for the user.
   2. Write a handoff with handoff:create-handoff. Don't perform it.
   3. Set your state file's `handoff:` field to its path, and add a Log line.
   4. Reply to <this session's ListAgents name> with one line: handoff <handle> <path>
   ```

   Deliver it the way dispatch.md § Relay does, fallback included. For a session reached
   through `workmux send`, also send SendMessage with no message and
   `notify_when_idle: true`, so its idle notice still arrives. Log each request in the
   session's `## Log` the way Relay does.

   Then reply with the sessions asked and the channel used for each, and say: "I'll write
   the hub handoff when they've all answered. Say 'write it now' to stop waiting." End the
   turn.
4. **Collect.** When a reply or an idle notice arrives from a session that was asked, read
   its state file and record one of these:
   - **new**: its `handoff:` changed after the request. Use that path.
   - **reply only**: it replied with a path but its `handoff:` didn't change. Use the
     path from the reply, and add a Drift line: "<handle>: replied with <path>, but
     `handoff:` still names <old path>". Don't edit its file.
   - **no reply**: it went idle, or its subscription expired, with neither. Use its current
     `handoff:` path. A later reply replaces this entry.

   An expired subscription is the timeout. Nothing else is needed to stop waiting on a
   session. Once every session asked has an entry, or the user says "write it now" (the rest
   are then "no reply"), go to step 5.
5. **Write the hub handoff.** Invoke `handoff:create-handoff` with this focus: "resume the
   hub at <hub-dir> with `/hub resume`; the hub appends the sessions, the queue and drift,
   so leave those out". Then append `templates/hub-handoff.md` to the written file with the
   Edit tool, with every placeholder filled:
   - **Sessions:** one row for each session asked, in stack order and then ad hoc. The
     last column holds the step 4 entry.
   - **Waiting on you:** the list from `hub.md`, verbatim.
   - **Relays not sent:** each relay this conversation drafted or discussed that hasn't
     gone out yet, and what it waits on.
   - **Drift:** refresh's Drift lines and the lines from step 4.
   - **Key facts:** what this conversation knows that no state file holds, such as what
     shipped, tickets filed, workarounds in use, and rulings the user made.
6. **Record.** Append `- <YYYY-MM-DD> handoff <path>` to the History in `stack.md`.
7. **Reply** with the hub handoff's path, one line per session (handle and entry), and how
   to resume: run `/clear`, then `/hub resume`.

**No SendMessage?** Say so in one line, skip steps 3 and 4, and write the hub handoff right
away from the files. Every row in the table is marked "not asked" and uses its current
`handoff:` path.

## Resume

`resume [<hub handoff path>] [--project <slug>]`

1. **Which handoff.** Use the path given. Otherwise use the path on the latest `handoff`
   line in `stack.md`'s History. If neither exists, say so and stop. Read the hub handoff:
   its Key facts and Relays not sent are this session's context from here on.
2. **Refresh**, following refresh.md, without the reply. This claims the hub for this
   session.
3. **Plan.** For each row in the handoff's Sessions table whose state file is still in
   `sessions/` (not `_done/`), take the handoff path from the state file's `handoff:`,
   because the worker may have written a newer one. Fall back to the table's path. Then pick
   one of these:
   - **relay**: ListAgents lists the session.
   - **open**: ListAgents doesn't list it, and `workmux list` shows its worktree.
   - **can't resume**: there's no worktree, or the handoff file is gone (handoff docs are
     pruned after 7 days).

   Show the plan, one line per session, and the relay message. Ask for one yes for the
   whole plan.
4. **Relay.** Use dispatch.md § Relay with: "From the hub: the user asks you to resume from
   your handoff, <path>. Read it, bring your state file up to date, and carry on."
5. **Open.** Run `workmux open <handle> -n -p "Read the handoff document at <path> and
   continue the work it describes. Your hub state file is <hub-dir>/sessions/<handle>.md."`
   `-n` opens a new window even when the old one still holds a stopped agent. If the new
   agent starts without the prompt, send it with `workmux send <handle> "<same text>"`. Clear the
   state file's `session:` field, which is the hub's, so the next refresh fills in the new
   name. Add a Log line: `<time> reopened by <this session> from <path>`.
6. **Refresh** again, and reply with how each session was resumed, the ones that couldn't
   be (and why), the "Waiting on you" list, and any relays not sent. Those still need the
   user's yes.

**No Bash?** Relay to the live sessions, and list the others with the `workmux open`
command for the user to run.
