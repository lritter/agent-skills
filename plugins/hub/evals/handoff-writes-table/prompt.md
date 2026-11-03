---
description: "/hub handoff with no SendMessage and stand-in handoff skills: writes the hub handoff at once with a resume table of the four pending sessions, each marked not asked with its current handoff path, no rows for done sessions, the Waiting on you list in order, and a handoff line in stack.md's History; perform-handoff never runs."
plugins: ["../..", "fixtures/handoff"]
max_turns: 40
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

/hub handoff
