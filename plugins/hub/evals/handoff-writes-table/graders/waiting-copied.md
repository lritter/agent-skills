---
type: regex
# The Waiting on you list is carried over in stack order, then age.
pattern: 'Waiting on you[\s\S]*?sign off on the plan[\s\S]*?merge #12[\s\S]*?rule on review findings[\s\S]*?close STH-300'
flags: i
target: { source: file, path: handoffs/handoff-eval.md }
---
