---
type: regex
# 1:1s by title pattern, privacy placeholders and all-day events stay out of the draft block.
pattern: '```(?:text)?\s*\n\s*Did:(?:(?!```)[\s\S])*(?:Moin|\bBusy\b|Private appointment|Conference week|1:1 Sam)'
match: not_contains
---
