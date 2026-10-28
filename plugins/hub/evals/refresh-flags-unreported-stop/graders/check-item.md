---
type: regex
# The idle-but-running review shows up in Waiting on you as a check, before the Stack section.
pattern: '^## Waiting on you[^\n]*\n(?:(?!^## )[\s\S])*?sth-104-alpha-review(?:(?!^## )[\s\S])*?^## Stack'
flags: mi
target: { source: file, path: .local/ai/hub/hub.md }
---
