---
type: regex
# A resume instruction, and one row per pending session: its current handoff path, marked not asked.
pattern: '^(?=[\s\S]*/hub resume)(?=[\s\S]*\|\s*`?sth-101-alpha-api`?\s*\|[^\n]*/tmp/handoff-sth-101-alpha-api\.md[^\n]*not asked)(?=[\s\S]*\|\s*`?sth-201-beta-ui`?\s*\|[^\n]*/tmp/handoff-sth-201-beta-ui\.md[^\n]*not asked)(?=[\s\S]*\|\s*`?sth-102-alpha-rollout`?\s*\|[^\n]*/tmp/handoff-sth-102-alpha-rollout\.md[^\n]*not asked)(?=[\s\S]*\|\s*`?sth-104-alpha-review`?\s*\|[^\n]*/tmp/handoff-sth-104-alpha-review\.md[^\n]*not asked)'
flags: i
target: { source: file, path: handoffs/handoff-eval.md }
---
