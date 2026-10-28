---
type: regex
pattern: 'state: done\s*\n[\s\S]*after_merge: \[run the backfill tool in prod\]'
target: { source: file, path: .local/ai/hub/sessions/sth-202-beta-cleanup.md }
---
