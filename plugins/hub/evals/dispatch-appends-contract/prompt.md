---
description: "/hub dispatch --serves Beta with stand-in handoff skills: the written handoff ends with the Reporting back block naming the state file and states, and sessions/sth-205-beta-export.md exists as queued, serving Beta, kind implement."
plugins: ["../..", "fixtures/handoff"]
max_turns: 40
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

/hub dispatch STH-205 build the beta export page --serves Beta
