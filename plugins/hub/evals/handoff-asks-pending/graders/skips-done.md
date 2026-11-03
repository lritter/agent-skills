---
type: regex
# Done sessions aren't asked, including the done one with a leftover after_merge step.
pattern: 'to:\s*`?sth-(?:103-alpha-done|202-beta-cleanup)'
match: not_contains
target: trace
---
