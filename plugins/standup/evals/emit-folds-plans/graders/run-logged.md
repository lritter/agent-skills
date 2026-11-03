---
type: regex
# One emitted line appended, keeping nothing else broken.
pattern: '^\| 2026-11-02T\d\d:\d\d(?::\d\d)?-05:00 \| emitted \|\s*$'
flags: m
target: { source: file, path: home/.local/ai/standup/log.md }
---
