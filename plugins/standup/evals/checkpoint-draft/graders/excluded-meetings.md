---
type: regex
# Private, 1:1, declined, focus, solo and unanswered events stay out of the draft block.
pattern: '```(?:text)?\s*\n\s*Did:(?:(?!```)[\s\S])*(?:Therapy|Vendor pitch|1:1 with|Focus time|Coffee hold|Offsite logistics)'
match: not_contains
---
