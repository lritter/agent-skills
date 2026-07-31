---
name: create-handoff
description: Use when only a handoff document is needed — for later use, archival, or when dispatched as a subagent to dump session state. Writes the document to a file but does not execute the handoff.
---

# Create Handoff

Write a handoff document summarizing the current conversation so another agent can continue the work.

Save it to `/tmp/handoff-TIMESTAMP-RANDOM.md` where TIMESTAMP is current epoch seconds (`date +%s`) and RANDOM is 4 hex chars (`openssl rand -hex 2`). The path is unique by construction — write directly with the Write tool.

Do not duplicate content already captured elsewhere (plan files under `.local/ai/plans/`, PRDs, tickets, design docs). Reference them by path or URL.

If any skills apply to the next session's focus, name them.

If the user passed arguments, treat them as hints about the focus of the new session.

Return the path of the file you wrote. Do not act on it.

## What to include

Adapt to context — skip sections that don't apply.

- **Goal** — what we're trying to accomplish
- **References** — plan files, PRDs, tickets, anchor docs the user pointed you to
- **Completed** — milestones reached this session
- **Current state** — branch, test status, blockers
- **Remaining work** — keep brief if a referenced plan file already covers it
- **Key decisions** — choices that shouldn't be re-debated
- **Notes** — gotchas that would otherwise be lost
- **Suggested skills** — for the next session, if any apply

Aim for a routing document — point to where state lives, rather than restating it.
