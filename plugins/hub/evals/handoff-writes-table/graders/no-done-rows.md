---
type: regex
# Done sessions get no row in the resume table.
pattern: '\|\s*`?sth-(?:103-alpha-done|202-beta-cleanup)`?\s*\|'
match: not_contains
target: { source: file, path: handoffs/handoff-eval.md }
---
