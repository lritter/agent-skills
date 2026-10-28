---
description: "/hub dispatch without --serves: asks which stack project (Alpha, Beta) or ad hoc the session serves before writing a handoff or starting anything."
plugins: ["../.."]
max_turns: 20
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

/hub dispatch STH-205 build the beta export page
