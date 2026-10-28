---
type: regex
# The handoff ends with the contract: the state file path and the states.
pattern: 'Reporting back[\s\S]*sessions/sth-205-beta-export\.md[\s\S]*needs-user[\s\S]*after-merge'
target: { source: file, path: handoffs/handoff-eval.md }
---
