---
name: perform-handoff
description: Use when an existing handoff document needs to be applied to a target — return its contents, dispatch a subagent, or start a fresh session via /clear. Skip the handoff orchestrator if the doc and target are already known.
---

# Perform Handoff

Apply a handoff document. Caller specifies the target; if missing, ask.

## Targets

- **return** — print the path and contents. No further action.
- **subagent** — invoke the `Agent` tool with `subagent_type` `general-purpose` and the doc contents as the prompt.
- **new-session** — run `"${CLAUDE_SKILL_DIR}/bin/run-handoff.sh" --clear --delay 0.5 <path>` via Bash. Do not show the command to the user. Confirm: "Handoff sent. The new session will start in a moment."

If the target is missing or ambiguous, use `AskUserQuestion` with the three options.

## Fallback

If `run-handoff.sh` fails: print the doc path and tell the user to `/clear` and paste manually. The script also copies the prompt to the clipboard, so paste should work.
