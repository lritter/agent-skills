---
type: regex
# STH-50 is Released but no PR merged in the window: not shipped this window.
pattern: '```(?:text)?\s*\n\s*Did:(?:(?!```)[\s\S])*(?:Old onboarding|STH-50\b)'
match: not_contains
---
