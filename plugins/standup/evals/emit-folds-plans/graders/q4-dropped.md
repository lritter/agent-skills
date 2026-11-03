---
type: regex
# The bullet the user asked to drop is gone from the last Did/Doing block (the final list).
pattern: 'Did:(?:(?!```)[\s\S])*Q4 planning(?![\s\S]*```(?:text)?\s*\n\s*Did:)'
match: not_contains
---
