# Refresh and clean

## Claim

On refresh, find this session's ListAgents name (ListAgents prints "This session is <name>").
If `stack.md`'s `hub_session` differs:
- the old name is still listed by ListAgents → say so in one line ("<old> was the hub; this
  session takes over") and continue;
- either way, write the new `hub_session` and `claimed`, and append a `claim` history line.

If ListAgents isn't available, leave the claim as it is and say so.

## Sources, in order

1. `stack.md`, `adhoc.md`, every `sessions/*.md` (not `_done/`).
2. `workmux list` — which worktrees exist (match the PATH column's basename to `handle`) —
   and `workmux status` — whether each agent is `working`, `waiting` or `done` (stopped).
3. `gh pr list --author @me --state all --limit 30 --json number,title,state,url,headRefName,mergedAt`
   plus `gh pr view <n> --json state,mergedAt,url` for any PR named in a state file and
   missing from that list.
4. ListAgents — fill each state file's missing `session:` with the listed name whose prefix
   is the handle (names carry a short suffix, e.g. `sth-1661-review-de`). One match only;
   on several, leave it blank and add a Drift line.

Read no Notion. Anything that couldn't be read goes in `## Sources`.

## Stopped without reporting

A session whose file says `queued` or `running` while workmux shows its agent `done` or
`waiting` (or ListAgents shows it `idle`) has probably stopped to ask the user something and
skipped its state update. Put it in "Waiting on you" as **"Check <session>: stopped without
reporting"**, after that project's other items, with `where` = its session name. Never leave
it out of the queue, and never change its state file. Without workmux or ListAgents, say in
`## Sources` that unreported stops couldn't be checked, so "Nothing is waiting on you" is
never claimed on files alone.

## Drift (report, don't fix)

- state `queued`/`running`/`needs-user` and no worktree for the handle;
- the session's PR is merged but state is `queued`, `running` or `needs-user`;
- state `running` and `updated` older than 24 hours;
- a state file with `serves` naming no stack project (treat it as ad hoc);
- an `adhoc.md` item whose PR merged or closed (offer to remove it).

## Write hub.md

Build it in the format in files.md § hub.md, replacing the whole file. Children nest under
their parent when the parent is another session in this hub; otherwise list them flat.

## Reply

1. The numbered "Waiting on you" list, exactly as in `hub.md` (or "Nothing is waiting on you").
2. One line per stack project: `<n>. <Project> — <Now, in a few words>`.
3. Drift, if any, as short lines.

Keep it scannable; the detail is in `hub.md`.

## Clean

1. Refresh first (without the reply).
2. Candidates: state `removable`, or `done` with an empty `after_merge`.
3. For each candidate, also check its PR is merged or closed (or it had none), and that no
   other live session names it as `parent` with open work. If either fails, it isn't a
   candidate; say why.
4. Show the candidates and the reason each other session stays (state, open `after_merge`
   steps). Ask which to remove.
5. For each confirmed one: `workmux remove <handle>` (add `-f` only if the user says so after
   a warning that it closes the agent's window and deletes the branch), then move its state
   file to `sessions/_done/`.
6. Refresh `hub.md` and report what was removed.

Never merge as part of clean.
