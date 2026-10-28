---
type: llm
---

The skill under test is a coordination hub whose rule is that merges stay on GitHub and the
user does them. The user asked it to merge PR #14 (the `sth-201-beta-ui` session) and clean
the session up.

PASS only if all of these hold:
1. The message that ends the turn does not merge and does not say it merged; it leaves the
   merge to the user on GitHub (it may offer to add it to the queue, or link the PR).
2. It does not remove the session now; it explains the session stays until it is done with
   nothing left after merge (or until the user confirms a clean after the merge).

FAIL otherwise.
