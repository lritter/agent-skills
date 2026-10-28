---
type: regex
pattern: '^(?=[\s\S]*^state: queued\s*$)(?=[\s\S]*^serves: Beta\s*$)(?=[\s\S]*^kind: implement\s*$)(?=[\s\S]*^ticket: STH-205\s*$)'
flags: m
target: { source: file, path: .local/ai/hub/sessions/sth-205-beta-export.md }
---
