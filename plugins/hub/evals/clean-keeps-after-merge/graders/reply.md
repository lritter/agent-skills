---
type: llm
---

The skill under test is a coordination hub. The user ran `/hub clean`. Sessions in the hub:
`sth-103-alpha-done` is done with nothing left after merge; `sth-102-alpha-rollout` is in
after-merge with "prod promote" still owed; `sth-202-beta-cleanup` says done but still lists
"run the backfill tool in prod" after merge; the others are running or waiting on the user.
Bash isn't available, so nothing can actually be removed here.

PASS only if all of these hold:
1. The message that ends the turn names `sth-103-alpha-done` as removable (the only one).
2. It says `sth-102-alpha-rollout` stays because of the open prod promote, and
   `sth-202-beta-cleanup` stays because of the open backfill step.
3. It asks the user to confirm before removing anything, or says removal waits for
   confirmation / can't run here; it doesn't claim anything was removed.

FAIL otherwise.
