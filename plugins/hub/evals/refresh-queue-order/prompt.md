---
description: "/hub with a two-project stack: regenerates hub.md with Waiting on you in stack order then age (Alpha plan sign-off, then Beta merge #12 and review ruling, then the projectless close STH-300), leaves every worker state as it was, and replies with the numbered list."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

/hub
