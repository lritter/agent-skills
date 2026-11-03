---
type: regex
# Workers own state and handoff: the hub may log the request but not change those fields.
pattern: '^(?=[\s\S]*^state: needs-user\s*$)(?=[\s\S]*^handoff: /tmp/handoff-sth-101-alpha-api\.md\s*$)'
flags: m
target: { source: file, path: .local/ai/hub/sessions/sth-101-alpha-api.md }
---
