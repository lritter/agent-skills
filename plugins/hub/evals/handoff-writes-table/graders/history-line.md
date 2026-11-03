---
type: regex
pattern: '^- \d{4}-\d{2}-\d{2} handoff \S*handoff-eval\.md'
flags: m
target: { source: file, path: .local/ai/hub/stack.md }
---
