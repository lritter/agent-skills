---
name: perform-handoff
description: Use when an existing handoff document needs to be applied to a target — return its contents, dispatch a subagent, start a fresh session via /clear, or start an agent in a new workmux worktree. Skip the handoff orchestrator if the doc and target are already known.
---

# Perform Handoff

Apply a handoff document. Caller specifies the target; if missing, ask.

## Targets

- **return** — print the path and contents. No further action.
- **subagent** — invoke the `Agent` tool with `subagent_type` `general-purpose` and the doc contents as the prompt.
- **new-session** — run `"${CLAUDE_SKILL_DIR}/bin/run-handoff.sh" --clear --delay 0.5 <path>` via Bash. Do not show the command to the user. The script queues the doc for the next session; the plugin's `SessionStart` hook points that session at it. It never types the doc into the pane, and it keeps the doc on disk.
  - If the output says "Handoff scheduled": confirm "Handoff sent. The new session will start in a moment."
  - If it says "not in tmux": tell the user to run `/clear` (or quit and restart `claude` in this project) and then send any message, e.g. `continue`.
- **workmux** — run `"${CLAUDE_SKILL_DIR}/bin/workmux-handoff.sh" --branch <branch> [--after "<command>"] <path>` via Bash, from the repository the work belongs in. The caller supplies the branch, and optionally the command the new agent runs once it has read the doc (e.g. `/st implement STH-123`); if the branch is missing, ask. The script branches from a freshly fetched origin default branch (`--base <ref>` overrides), creates the worktree and its tmux window in the background, and starts the agent with the doc as its first prompt. The current session keeps going.
  - On success: relay the handle it prints, and say the agent is running in the background.
  - On failure: relay the error. If the branch or worktree already exists, ask for another branch name, or whether to open the existing one (`workmux open <handle>`).

If the target is missing or ambiguous, use `AskUserQuestion` with the four options.

## Fallback

If `run-handoff.sh` fails, or the new session didn't pick up the handoff (the pending handoff expires after 10 minutes): print the doc path and tell the user to `/clear` and enter `Read the handoff document at <path> and continue the work it describes.` The doc stays on disk for 7 days, so a failed handoff can be retried.
