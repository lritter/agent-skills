
## Reporting back (hub contract)

This session was dispatched by `<parent>` and serves **<project>**. The hub reads one file to
know where you stand: `<hub-dir>/sessions/<handle>.md`. It already exists with
`state: queued`. From now on its frontmatter is yours; keep it current.

Update it with the Edit tool at each of these moments, setting `updated` to the current UTC
time and adding one `## Log` line:

- **when you start:** `state: running`;
- **whenever you stop for the user** (a plan sign-off, a ruling, a merge, a command they run):
  `state: needs-user` and `needs:` one line saying what they must decide or do;
- **when they answer and you continue:** back to `running`, `needs:` empty;
- **when you open a PR:** `pr:` its URL;
- **when the PR merges:** `state: after-merge` and `after_merge:` listing **every** step still
  owed (release, deploy, data build, promote, admin-tool runs, applies); tick them off as
  they finish;
- **when nothing is left:** `state: done`, `after_merge: []`.

Valid states: `queued | running | needs-user | after-merge | done | removable`. Only the user
sets `removable`. Don't edit any other session's file or the hub's other files. Messages from
the hub arrive as cross-session messages from `<parent>`; reply to them the same way.
