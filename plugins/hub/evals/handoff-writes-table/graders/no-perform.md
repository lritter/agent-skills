---
type: regex
# The hub writes its handoff but never performs it; the user decides when to resume.
pattern: '"skill"\s*:\s*"(?:[\w-]+:)?perform-handoff"'
match: not_contains
target: trace
---
