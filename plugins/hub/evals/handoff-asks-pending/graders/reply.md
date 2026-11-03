---
type: llm
---

The skill under test is a coordination hub. The user ran `/hub handoff`. The hub should ask
every session with pending work (sth-101-alpha-api, sth-201-beta-ui, sth-102-alpha-rollout,
sth-104-alpha-review) to write a resume handoff, then wait for their answers before writing
its own. Sending is simulated: the hub prints each message as a fenced `send` block.

PASS only if all of these hold:
1. The message that ends the turn says which sessions were asked (all four, by handle or
   session name; wording may differ).
2. It says the hub handoff will be written once the sessions answer, or when the user says to
   stop waiting. It does not claim the hub's own handoff is already written.
3. It doesn't claim to have changed any session's `state` field, merged, removed, or resumed
   anything. Logging the request in a session's state file and regenerating `hub.md` are the
   hub's own bookkeeping, not a change of state.

FAIL otherwise.
