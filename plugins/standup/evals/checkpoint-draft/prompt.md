---
description: "/standup on a Monday with no run log: one checkpoint message with a Did/Doing draft since Friday and both questions; private, declined, unanswered, 1:1 and focus events, DMs, private channels, excluded channels, one-liners and a Released ticket with no merged PR stay out; no run log written."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash and the MCP tools (calendar, Notion, Slack) cannot run in this session. Their responses are files under fixtures/: read fixtures/README.md for which file stands in for which call, and read that file wherever the skill makes the call. `~` is ./home here, so the config is at home/.local/ai/standup/config.md. Your GitHub login is `me`. Now is Monday 2026-11-02 09:30 America/New_York. AskUserQuestion is not available; ask in plain text."
---

/standup
