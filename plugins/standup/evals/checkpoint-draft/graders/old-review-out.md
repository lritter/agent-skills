---
type: regex
# example/web#9 was reviewed in September; a bot touched it since. Not in this window's draft.
pattern: '```(?:text)?\s*\n\s*Did:(?:(?!```)[\s\S])*(?:web/pull/9\b|web#9\b|Legacy theme)'
match: not_contains
---
