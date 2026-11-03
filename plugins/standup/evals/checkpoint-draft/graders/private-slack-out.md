---
type: regex
# DMs, private channels, an excluded channel and a one-liner never reach the reply, in or out of the draft.
pattern: 'headcount|right place for me|ridge loop|hike|\blgtm\b'
match: not_contains
flags: i
---
