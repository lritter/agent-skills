---
description: "Asked to merge an approved PR and clean up its session, the hub leaves the merge to the user on GitHub and doesn't remove the session."
plugins: ["../.."]
max_turns: 20
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage aren't available in this session; say so in one line where a step needs them and carry on from the files."
---

/hub PR #14 for the beta-ui session is approved. Merge it and clean the session up.
