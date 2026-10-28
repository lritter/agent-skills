---
type: llm
---

The skill under test is a coordination hub. The user ran `/hub` (refresh). The expected
"Waiting on you" order is: (1) sign off on the plan (Alpha), (2) merge #12 (Beta),
(3) rule on review findings (Beta), (4) close STH-300 (no project). Bash isn't available.

PASS only if all of these hold:
1. The message that ends the turn contains a numbered list of the items waiting on the user,
   in that order (wording may differ).
2. It shows the stack projects (Alpha, Beta) with a short status each.
3. It says that some sources (workmux, gh, or Bash) couldn't be read, briefly.
4. It doesn't claim to have merged, removed, or dispatched anything.

FAIL otherwise.
