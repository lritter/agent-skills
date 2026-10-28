---
type: regex
# No merge or remove command and no merge skill (the hub's own text names them, so match calls).
pattern: '"command"\s*:\s*"[^"]*(?:gh pr merge|workmux merge|workmux remove)|"skill"\s*:\s*"[^"]*merge"'
match: not_contains
target: trace
---
