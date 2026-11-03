---
description: "/standup with today's plans in the arguments and the change answer pre-supplied: emits the final list in a fenced text block, folds the plans into Doing, drops the bullet the user asked to drop, and appends one emitted line to the run log."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash and the MCP tools (calendar, Notion, Slack) cannot run in this session. Their responses are files under fixtures/: read fixtures/README.md for which file stands in for which call, and read that file wherever the skill makes the call. `~` is ./home here, so the config is at home/.local/ai/standup/config.md. Your GitHub login is `me`. Now is Monday 2026-11-02 09:30 America/New_York. AskUserQuestion is not available; ask in plain text. This run is non-interactive. The user's answer to the checkpoint is already known: Drop the Q4 planning meeting, everything else is fine. Show the checkpoint, treat that as the reply, and go straight on to Emit in the same turn."
---

/standup finish the importer runbook and pair with Priya on export pagination
