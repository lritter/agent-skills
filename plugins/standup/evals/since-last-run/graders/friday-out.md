---
type: regex
# Work before the last run belongs to the previous standup.
pattern: '```(?:text)?\s*\n\s*Did:(?:(?!```)[\s\S])*(?:STH-101\b|Eng sync|Q4 planning|api/pull/40\b)'
match: not_contains
---
