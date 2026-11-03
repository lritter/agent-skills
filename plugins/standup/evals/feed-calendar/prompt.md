---
description: "/standup with the work calendar configured as an imported ICS feed (no attendees, no response status, all public): the all-hands, a customer call and the leadership meeting are kept; a <> 1:1, a 1:1 titled 1:1, Busy and Private appointment placeholders and an all-day event stay out; the draft says feed attendance isn't verified."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash and the MCP tools (calendar, Notion, Slack) cannot run in this session. Their responses are files under fixtures/: read fixtures/README.md for which file stands in for which call, and read that file wherever the skill makes the call. `~` is ./home here, so the config is at home/.local/ai/standup/config.md. Your GitHub login is `me`. Now is Monday 2026-11-02 09:30 America/New_York. AskUserQuestion is not available; ask in plain text."
---

/standup
