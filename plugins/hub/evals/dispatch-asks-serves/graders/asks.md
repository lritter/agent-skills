---
type: llm
---

The skill under test is a coordination hub. The user ran `/hub dispatch STH-205 build the
beta export page` without `--serves`. The stack has two projects, Alpha and Beta.

PASS only if all of these hold:
1. The message that ends the turn asks which project the new session serves, offering the
   stack's projects (Alpha, Beta) and ad hoc. Suggesting Beta as the likely answer is fine.
2. It hasn't started a session or written a handoff yet.

FAIL otherwise.
