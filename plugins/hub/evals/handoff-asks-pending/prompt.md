---
description: "/hub handoff with a SendMessage stand-in: asks the four pending sessions (needs-user, after-merge, running) to write a handoff with create-handoff and set their own handoff field, skips the two done ones, leaves every state file's fields alone, and ends the turn waiting for answers."
plugins: ["../.."]
max_turns: 30
runs: 2
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: "ListAgents and Bash aren't available in this session; say so in one line where a step needs them and carry on from the files. SendMessage can't reach other sessions here. For each message you would send with it, print a fenced block that opens with ```send, then a line `to: <session name>`, then the message, instead of calling the tool. Treat each printed block as delivered, with an idle notice still to come."
---

/hub handoff
