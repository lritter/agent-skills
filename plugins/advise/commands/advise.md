---
description: Consult a fable reviewer that reads this session's full transcript and advises on your approach
argument-hint: "[optional focus, e.g. the migration approach]"
allowed-tools: Bash(find:*)
disable-model-invocation: true
---

This session's transcript file is:

!`find "$HOME/.claude/projects" -name "${CLAUDE_CODE_SESSION_ID}.jsonl" 2>/dev/null`

If the line above is blank (session id unset or transcript not yet written),
stop and tell the user you couldn't locate the transcript — do not dispatch a
reviewer at an empty path.

Dispatch the fable-advisor subagent to read that transcript file and advise on the
current approach. Use `subagent_type: "advise:fable-advisor"` (this plugin ships the
agent namespaced under the plugin name); if your harness reports that type isn't
found, fall back to the bare `subagent_type: "fable-advisor"`. In the prompt you
give it, include:

- The absolute transcript path printed above.
- Any focus the user named: $ARGUMENTS
  (If empty, ask it for a general review of the current approach and pending decision.)

When it returns, relay its advice to the user concisely and give it serious weight
— treat it exactly as you would the built-in `advisor` tool's output. If you
disagree based on primary evidence, surface the conflict rather than silently
overriding it.
