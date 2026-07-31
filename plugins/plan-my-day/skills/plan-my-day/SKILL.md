---
name: plan-my-day
description: Morning planning routine — reads calendar, PRs, tickets, email, and Apple Reminders, checks standing priorities against the week so far, and produces one clear agenda for today. Run manually.
disable-model-invocation: true
---

# Plan My Day

Produce **one agenda for today**, grounded in what is actually on the calendar and actually waiting on the user — and make sure the standing priorities (exercise, music, side projects, whatever they've named) get real time, not leftovers.

## The contract

Three phases, one interactive checkpoint. That budget is the point of the skill — a morning planner that turns into a conversation has failed.

1. **Gather** — every source read in parallel, one wave. No questions.
2. **Checkpoint** — a *single* message: confirm yesterday's commitments, surface conflicts, ask only what's genuinely ambiguous.
3. **Emit** — agenda to terminal and file, ledger updated, calendar writes offered.

Do not ask a question in phase 1. Do not go back for a second round in phase 2 unless the answer invalidates the plan. If you find yourself on a third exchange, stop and emit the agenda with the ambiguity flagged in it.

## State

Two hand-editable files under the state directory (`~/.local/ai/agenda/` by default):

- **`config.md`** — working hours, hard stops, calendar IDs, Reminders lists, issue-tracker source, and the standing priorities with their weekly cadence targets. Read it first; everything else depends on it. **Every account-specific value lives here, never in this skill.**
- **`log.md`** — the ledger of standing-priority commitments, one row per priority per day, status `planned` → `done` | `skipped`. This is what makes week-awareness work.

If `config.md` does not exist, copy `reference/config.template.md` into place, then walk the user through filling it in — that *is* the whole first run. Don't try to plan a day against a template.

### How cadence is computed

**The week starts Monday.** "4x/week" means four `done` rows dated Monday through Sunday of the current week.

Only `done` counts. `skipped` and `planned` do not. A `planned` row dated before today is *unresolved* — ask about it at the checkpoint; if it goes unanswered, record `unknown` and don't count it.

**Row format — write it exactly like this, unpadded:**

```
| 2026-07-31 | exercise | planned |
```

One space either side of each pipe, ISO date, priority name lowercase and matching `config.md`. Resolving a row is an `Edit` that swaps only the status token (`planned` → `done`). That match is exact and literal, so a row written with different padding on one run cannot be resolved on the next — never pad the columns to align them, however much nicer the table looks.

Worked example. Today is Friday 2026-07-31, so the week began Monday 2026-07-27:

```
| 2026-07-27 | exercise | done |
| 2026-07-28 | music | done |
| 2026-07-29 | exercise | skipped |
| 2026-07-30 | exercise | done |
| 2026-07-30 | music | planned |
```

- **exercise** — 2 done (27, 30) against a target of 4 → `2/4`. Three days remain including today, and two sessions are needed. Feasible only if one lands today, so it's **behind — place it today**.
- **music** — 1 done (28) against 2, plus an unresolved `planned` on the 30th → ask whether that happened. If yes, `2/2`, done for the week. If no, `1/2` with two days left → **on pace**, no need to force it today.

"Behind" is not simply *count < target*. It means the remaining days in the week are no longer enough to hit the target unless today is used. Say which of the two it is — a priority at `1/4` on Monday is on pace; the same number on Friday is not recoverable, and the honest move is to say so rather than cram it.

**On the first run the ledger is empty.** Don't infer anything from that or report every priority as behind — say the ledger is new and start recording from today.

## Phase 1 — Gather

Load every deferred tool in **one** `ToolSearch` call. One call, not one per tool:

```
select:mcp__claude_ai_Google_Calendar__list_events,mcp__claude_ai_Google_Calendar__create_event,mcp__claude_ai_Gmail__search_threads,mcp__plugin_Notion_notion__notion-query-data-sources
```

`list_calendars` is deliberately absent — config stores calendar IDs directly, so the normal path never needs to resolve names. Only the first-run bootstrap does; load it separately there.

Then fan out. These are independent — issue them in a single block so they run concurrently.

| Source | How |
| --- | --- |
| Config + ledger | `Read` config.md; read the trailing 7 days of log.md |
| Calendar — today | `list_events` for today across the calendar IDs in config |
| Calendar — week | `list_events` through end of week, for shape only (is Thursday already lost?) |
| PRs waiting on you | `gh search prs --review-requested=@me --state=open --limit 20 --json repository,number,title,author,updatedAt` |
| Your open PRs | `gh search prs --author=@me --state=open --limit 20 --json repository,number,title,isDraft,updatedAt` |
| Tickets | `notion-query-data-sources` against the source in config — see below |
| Email | `search_threads`, query below, `pageSize` 15 |
| Reminders | `reminders show "<list>" --format json` per list in config |
| Gym classes | `gym-schedule`'s `scripts/virtuagym_schedule.py`, `--date` today, once per **Schedule sources** entry in config. Skip entirely if that section is empty. |

Both `gh search` forms are repo-independent — they work from any directory, no repo context needed.

### The two queries that need to be exactly right

Both are wrong in their obvious formulation. These lessons cost a smoke test to find; don't rediscover them.

**Tickets.** Filtering a shared backlog by status alone returns other people's work. If the tracker has a department, team, or project relation, filter on it — but note that **`notion-query-data-sources` serializes a relation as a JSON array of page URLs**, so `LIKE '%Engineering%'` matches nothing. You must filter on the page *id*:

```sql
SELECT "Task ID", "Task name", "Status", "Priority"
FROM "<data_source from config>"
WHERE "Status" IN (<statuses from config>)
  AND "Department" LIKE '%<department id from config>%'
ORDER BY "Task ID" DESC
```

Measured on one real backlog: 37 rows → 16. Also check for rows where the relation is null — they're silently dropped by this filter, and if the result ever looks short that's the first thing to test (`AND "Department" IS NULL`).

**Email.** `is:unread newer_than:1d` returns hundreds of threads of newsletters, job alerts, and notification mail. Unread is not a signal. Use:

```
newer_than:2d in:inbox -category:promotions -category:social -category:updates
-category:forums -from:noreply -from:no-reply -from:notifications@github.com
```

Measured: ~200 threads → 4, all real. GitHub notifications are excluded deliberately — `gh` already covers PRs and the email copies are pure duplication. Add further `-from:` exclusions to config as recurring noise sources reveal themselves. From what's left, surface only threads where someone is waiting on a reply; note that a thread can come back without being unread, because Gmail matches threads by any message in them.

### Reading the other sources honestly

**Reminders.** Most have no `dueDate` — those are a *backlog to draw from*, not obligations. Only a `dueDate` on or before today is a commitment. Undated items are candidates to slot when there's room or when one matches a standing priority that's behind pace. Never present an undated reminder as due.

Requires [`reminders-cli`](https://github.com/keith/reminders-cli) (`brew install keith/formulae/reminders-cli`). Do not fall back to AppleScript: a per-item `osascript` loop over one 10-item list takes ~29s versus 0.47s for the CLI.

**All-day calendar events are context, not blocks.** A multi-day "kid at camp" or "X in town" spans days and consumes no specific hours. They change the shape of the day — who's home, what's possible — and belong in the agenda's opening line, never in the timed schedule.

**Events marked free do not consume time.** Check `availability` / `transparency` — `AVAILABILITY_FREE` or `transparent` means the slot is still open. Optional evening classes and reminder-style entries come back this way. Show them, but count their hours as available when finding gaps, or you'll conclude the day is full when it isn't.

**PRs.** Review-requested outranks authored. Cross-reference both against the ticket list: if PR titles carry the ticket id, a ticket with one of their open PRs is confirmed-theirs and ranks above a ticket that merely sits in *In progress*.

### Degrade loudly

If a source fails — expired MCP auth, calendar not connected, `gh` not logged in — the agenda says so explicitly:

```
Notion: NOT CHECKED — MCP auth expired, re-auth with /mcp
Gym schedule: NOT CHECKED — virtuagym_schedule.py exited 1
```

Never silently omit a source. An agenda quietly missing a 10am is worse than no agenda at all. MCP auth expires periodically; expect it.

## Phase 2 — The checkpoint

One message. Batch everything into it, using `AskUserQuestion` where the answers are closed-ended.

1. **Confirm the ledger.** Every `planned` row from the last few days that's still unresolved: did it happen? Update to `done` or `skipped`. Ask about all of them at once — this is the "did exercise actually happen" check, and it's the only reason week-awareness works.
2. **Report the week's standing.** For each standing priority, where it sits against cadence: `exercise 2/4 this week — behind`, `music 1/2 — on pace`. Short lines, no commentary.
3. **Flag the conflicts.** Overcommitment, a hard stop colliding with a meeting, a day with no gap big enough for a priority that's behind. State the problem and your proposed resolution together — don't ask an open question when you have a recommendation.

## Phase 3 — Emit

**Sequencing rule**, applied in order:

1. **Fixed** — calendar events. They're not negotiable, they're the frame.
2. **They are the blocker** — someone else's work is stalled on them. Review-requested PRs, email awaiting a reply, tickets in review. This outranks their own solo work, always.
3. **Behind-pace standing priorities** — a priority under its weekly cadence gets a real block today, not a hope. Protect it like a meeting.

   If config lists **anchored options** for a priority — a standing group run, a lesson slot — or a **schedule source** returned classes for today, prefer a slot that lands on one over an unanchored block. A block that maps to something scheduled in the world gets done; a floating "45m exercise" doesn't. If both sections are empty, slot into any qualifying gap and mention once, at most, that filling one in would help.
4. **Their own work in flight** — open PRs, tickets in progress.
5. **Backlog** — undated reminders, on-pace priorities, anything else, only if room remains.

Respect what the hard stop actually bounds. In most configs it bounds *work*, not the day — placing an evening standing priority after it is correct; placing a PR review there is not.

Then:

- Print the agenda to the terminal.
- Write it to `<agenda_dir>/YYYY-MM-DD.md`.
- Append today's standing-priority blocks to `log.md` as `planned`.
- **Offer the calendar writes.** Confirm before creating — one confirmation covering the batch is fine, but name every event it will create. Never create an event that wasn't in the agenda they just read.
- If a reminder was clearly completed, offer `reminders complete "<list>" <externalId>`. Confirm first.

### Agenda format

Times, then the thing, then why it's there. No filler.

```markdown
# Monday, August 3

**Shape:** Kid at camp all week. One 3h meeting, afternoon is open.
Exercise behind (2/4) — placed at 16:00.

## Fixed
- 09:00–12:00  Board meeting

## Blocking others
- Review acme/api#452 (waiting 5d) — 45m, 13:00
- Reply to the contractor re: amended plans — 10m, they're blocked on the estimate

## Standing priorities
- 16:00  Exercise — behind pace, 2/4 this week

## In flight
- #456 migration gate — finish the CI path, 14:00–15:30

## Not today
- Geocode prod standup — no gap big enough after the board meeting

## Sources
Calendar ✓ · PRs ✓ · Notion ✓ · Gmail ✓ · Reminders ✓
```

The **Not today** section is not optional. Naming what got cut is how the agenda stays honest about being a plan rather than a wish.
