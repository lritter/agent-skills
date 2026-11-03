---
type: regex
# A printed request (a send block with a session name) names create-handoff.
pattern: '```send\s*(?:\\n)?\s*to:\s*`?sth-(?:(?!```)[\s\S])*create-handoff'
target: trace
---
