---
type: regex
# Waiting on you, in stack order then age: Alpha's sign-off, Beta's merge #12 (10-20) before
# its review ruling (10-26), then the projectless close STH-300; all before the Stack section.
pattern: '^## Waiting on you[^\n]*\n[\s\S]*?sign off on the plan[\s\S]*?merge #12[\s\S]*?rule on review findings[\s\S]*?close STH-300[\s\S]*?^## Stack'
flags: mi
target: { source: file, path: .local/ai/hub/hub.md }
---
