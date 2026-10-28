---
type: regex
# create-handoff runs before perform-handoff.
pattern: '"skill"\s*:\s*"(?:[\w-]+:)?create-handoff"[\s\S]*"skill"\s*:\s*"(?:[\w-]+:)?perform-handoff"'
target: trace
---
