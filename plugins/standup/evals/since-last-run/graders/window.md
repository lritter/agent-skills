---
type: llm
---

The skill under test writes a daily standup. Now is Tuesday 2026-11-03 09:30 and the run log's
last line is Monday 2026-11-02 09:40, so "Did" covers Monday 09:40 to now. The Slack search
fixture returns an auth error.

PASS only if all of these hold:
1. The message that ends the turn shows a Did/Doing draft and says the window starts at the
   last run on Monday (wording may differ).
2. Did includes STH-102 (Importer retries on 429) as shipped and the Incident retro.
3. Did does not include Friday's items: STH-101 / Export endpoint streams CSV, Eng sync,
   Q4 planning, the review of example/api#40.
4. It says Slack was not checked because of the auth error, rather than leaving Slack out
   silently.
5. Doing includes the 11:00 Design review, and leaves out Offsite logistics and 1:1 with Priya.

FAIL otherwise.
