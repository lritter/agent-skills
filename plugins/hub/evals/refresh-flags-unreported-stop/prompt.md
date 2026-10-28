---
description: "/hub where sth-104-alpha-review's file says running but workmux shows its agent done: the queue gets a check item for it (after Alpha's sign-off), its state file is left as running."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "Bash, ListAgents and SendMessage can't run in this session. When a step needs one of them, don't run it; use these recorded results instead.\n\n`workmux list`: worktrees exist for every session in .local/ai/hub/sessions/.\n\n`workmux status`:\n```\nWORKTREE                STATUS   ELAPSED\nsth-101-alpha-api       done     3h\nsth-104-alpha-review    done     2h 10m\nsth-102-alpha-rollout   done     5h\nsth-201-beta-ui         done     1d\nsth-103-alpha-done      done     1d\nsth-202-beta-cleanup    done     2d\n```\n\n`gh pr list`: unavailable."
---

/hub
