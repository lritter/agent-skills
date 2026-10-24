---
name: work-on
description: Use when the user wants a piece of work started by a new agent in its own workmux worktree — "/work-on <what>", "spin this off into a worktree", "start an agent on STH-123". Writes a handoff for that work, then starts it in a background workmux window.
argument-hint: "<what to work on, e.g. STH-123 or a task description>"
---

# Work On

Start `$ARGUMENTS` in a new workmux worktree, with a handoff doc as the new agent's first prompt. The current session stays where it is.

You are a dispatcher. Use the context you already have; do not explore or read the codebase to write the handoff. The new agent does the work.

1. **Name the branch.** Follow the project's branch convention from its instructions (CLAUDE.md, rules). If the request names a ticket, use its id the way the convention does. Otherwise use a short kebab-case summary of the work. If the convention needs something the request doesn't give (e.g. a ticket id), ask. Don't use workmux's `-A` auto-naming.
2. **Pick the follow-up command, if any.** If the project's instructions name a skill or command for starting this kind of work (e.g. implementing a ticket), that is the `--after` command. Otherwise there is none.
3. **Write the handoff** with the `create-handoff` skill, with the request as its focus. Carry over what this conversation knows about the work (decisions, references, constraints). If the conversation has nothing on it, the doc is the request plus any references the user gave. Don't restate what the follow-up command will load itself (a ticket, a plan file).
4. **Perform it** with the `perform-handoff` skill, target **workmux**, passing the branch and follow-up command.

Report the branch, the handle, and the follow-up command in one or two lines.
