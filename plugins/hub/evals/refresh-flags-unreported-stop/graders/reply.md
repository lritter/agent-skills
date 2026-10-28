---
type: llm
---

The skill under test is a coordination hub. The user ran `/hub`. The session
`sth-104-alpha-review` says `running` in its state file, but workmux shows its agent stopped
(`done`), so it probably stopped to ask the user something without reporting.

PASS only if all of these hold:
1. The message that ends the turn lists the items waiting on the user, and among them is a
   check on `sth-104-alpha-review` (wording may differ: stopped without reporting, idle while
   running, needs a look).
2. It does not say the review is finished or removable.

FAIL otherwise.
