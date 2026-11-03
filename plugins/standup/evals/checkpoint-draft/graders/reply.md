---
type: llm
---

The skill under test writes a daily standup. The user ran `/standup` on Monday 2026-11-02 at
09:30 with no run log, so "Did" covers Friday 2026-10-30 through now. Sources are fixture files.

PASS only if all of these hold:
1. The message that ends the turn shows a draft with a "Did" list and a "Doing" list.
2. It says the window starts Friday (or the previous working day), in some wording.
3. It asks what the user plans to work on today, and whether anything in the draft should
   change. Both questions, in this message.
4. It does not present a final list as done, and doesn't say the standup was logged.
5. Did includes STH-101 as shipped and the review of example/api#40. Doing includes STH-104 or
   STH-103, and the 14:00 Incident retro.

FAIL otherwise.
