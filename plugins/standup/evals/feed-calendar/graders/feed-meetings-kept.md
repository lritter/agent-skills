---
type: regex
# A feed has no attendees, so the attendee and response rules must not drop its public meetings.
pattern: '```(?:text)?\s*\n\s*Did:(?=(?:(?!```)[\s\S])*All Hands)(?=(?:(?!```)[\s\S])*Northwind)(?=(?:(?!```)[\s\S])*Leadership Meeting)'
---
