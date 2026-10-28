---
description: "Plain-language trigger: asking what's waiting on me in a repo with a hub loads the hub skill."
plugins: ["../.."]
max_turns: 8
runs: 2
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

What's waiting on me right now across my sessions?
