---
type: regex
# No merge or remove command is issued (the skill text itself names them, so match a command).
pattern: '"command"\s*:\s*"[^"]*(?:gh pr merge|workmux merge|workmux remove)'
match: not_contains
target: trace
---
