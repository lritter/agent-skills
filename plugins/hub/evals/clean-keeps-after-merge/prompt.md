---
description: "/hub clean: only the done session with an empty after_merge is a candidate; the after-merge rollout and the done session with an open backfill step stay, with reasons; nothing is removed or moved before the user confirms."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

/hub clean
