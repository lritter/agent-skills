---
type: regex
# Every session with pending work is asked: two needs-user, one after-merge, one running.
pattern: '^(?=[\s\S]*to:\s*`?sth-101-alpha-api)(?=[\s\S]*to:\s*`?sth-201-beta-ui)(?=[\s\S]*to:\s*`?sth-102-alpha-rollout)(?=[\s\S]*to:\s*`?sth-104-alpha-review)'
target: trace
---
