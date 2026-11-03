---
description: "/standup on a Tuesday with a run logged Monday 09:40: the window starts at the last run, so Friday's work is out and Monday's merge and retro are in; Slack's auth error shows as a NOT CHECKED line; today's unanswered and 1:1 meetings stay out of Doing."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash and the MCP tools (calendar, Notion, Slack) cannot run in this session. Their responses are files under fixtures/: read fixtures/README.md for which file stands in for which call, and read that file wherever the skill makes the call. `~` is ./home here, so the config is at home/.local/ai/standup/config.md. Your GitHub login is `me`. Now is Tuesday 2026-11-03 09:30 America/New_York. AskUserQuestion is not available; ask in plain text."
---

/standup
