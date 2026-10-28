# Dispatch and relay

## Dispatch

`dispatch <what> --serves <project|adhoc> [--kind <kind>] [--base <ref>] [--project <slug>]`

Any session can dispatch, not only the hub; the dispatching session becomes the new
session's `parent`.

1. **Which hub.** If `--serves` names a project whose stack entry has a `hub:` path, the state
   file goes in that project hub's `sessions/`; otherwise in the main hub's.
2. **Kind.** `implement` (a ticket to build), `review` (review a PR; comments only, fixes go
   to the author via relay), `analysis`, `rollout` (post-merge release steps), or `other`.
   Infer it from the request; ask only if it's unclear.
3. **Branch and follow-up command.** Name the branch from the project's branch convention
   (its CLAUDE.md or rules); use a ticket id the way the convention does; ask if the
   convention needs something the request doesn't give. Pick the `--after` command the
   project's instructions name for this kind of work (e.g. an implement skill for a ticket),
   or none. For a review, base the branch on the PR's branch (`--base origin/<pr-branch>`).
4. **Handoff.** Invoke `handoff:create-handoff` with the request as its focus, carrying over
   what this conversation knows about the work (decisions, references, constraints).
5. **Contract.** Append `templates/reporting-back.md` to the written handoff with the Edit
   tool, verbatim, after filling its placeholders (`<hub-dir>`, `<handle>`, `<project>`,
   `<parent>`). The handle is the lowercased branch name. `<hub-dir>` is the path as the
   worker will see it: repo-relative (`.local/ai/hub`) when the local AI storage directory
   is a symlink shared by every worktree, otherwise absolute.
6. **Start it.** Invoke `handoff:perform-handoff` with target `workmux`, the branch, the
   `--after` command and `--base` if any. Use the handle it prints if it differs from step 5,
   and fix the block's paths to match.
7. **State file.** Write `sessions/<handle>.md` from `templates/session.md` with
   `state: queued`, `parent` (this session's ListAgents name; for a review of a PR whose
   author is a live session in this hub, the author session's name, so the review nests under
   it and its fixes relay there), `serves`, `kind`, `branch`,
   `ticket`, `handoff`, `updated`, and a Log line "dispatched by <parent> (queued)".
8. Reply with the branch, the handle, what it serves, and the follow-up command, in one or
   two lines.

If perform-handoff fails, don't write the state file; relay the error.

## Relay

`relay <session> <message>`

1. **Resolve the target.** `<session>` may be a handle, a ticket id, or a ListAgents name.
   Find its state file; use its `session:` name. Without one, run ListAgents and match by
   handle prefix. When the user says "send the fixes to the author" about a review, the
   target is the review session's `parent`.
2. **Send.** `SendMessage` to that name. Make the first line a self-contained sentence saying
   who it's from and what it is ("From the hub: ruling on your plan for STH-1604 — approved").
3. **Fallback.** If SendMessage fails, finds no match, or the result says the message is
   held for approval in the other session, write the message to a temp file in the
   scratchpad and run `workmux send <handle> -f <file>`. Say which channel was used. A held
   message is still delivered later; mention that the user may need to approve it there.
4. **Log.** Append to the session's `## Log`: `<time> relay from <this session>: "<first line>"`.

Never ask a session to do something this session isn't permitted to do.
