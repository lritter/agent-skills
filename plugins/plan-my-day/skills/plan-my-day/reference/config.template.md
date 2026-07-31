# plan-my-day config

Copy to `~/.local/ai/agenda/config.md` and fill in. Hand-edited — the skill reads
this every run and never writes to it. **All account-specific values live here**,
so the skill itself stays free of personal data.

## Paths

- `agenda_dir`: `~/.local/ai/agenda`
- `ledger`: `~/.local/ai/agenda/log.md`

## Day shape

- `working_hours`: 09:00–17:30
- `hard_stops`: 17:30 — say what it bounds. Usually it bounds *work*, not the
  day: an evening standing priority after it is fine, a PR review is not.
- `timezone`: America/New_York

## Calendars

Calendar **IDs**, not display names — get them from `list_calendars` once during
setup. Storing IDs is what lets the daily run skip that call.

- `you@example.com` — primary
- `family........@group.calendar.google.com` — family

Watch for calendars whose own timezone differs from yours; normalize before
placing anything on the agenda.

## Reminders lists

Read via `reminders show "<name>" --format json`. List only the ones that hold
actual tasks — shopping, packing, and wish lists are noise.

- Reminders
- Inbox

## Issue tracker

- `data_source`: `collection://<uuid>` — from `notion-fetch` on the database
- `statuses`: `In progress`, `In review`
- `department_filter`: `<page id>` — optional; if the backlog is shared with
  other teams, this is what keeps their work out. Filter on the page **id**, not
  the team's name: the relation serializes as a JSON array of URLs and the name
  never appears in it.

If the tracker has no assignee property, status plus a team filter is the best
available proxy for "mine" — say so rather than implying the list is complete.

## Extra email exclusions

Recurring senders that survive the default category filters. Appended to the
Gmail query as `-from:` terms.

- (add them as they reveal themselves)

## Standing priorities

Weekly cadence targets. The skill protects whichever is furthest behind pace.

| Priority | Target | Preferred slot | Notes |
| --- | --- | --- | --- |
| exercise | 4x/week | any gap ≥ 45min | |
| music | 2x/week | evening | |
| side projects | 1 block/week | weekend or a light afternoon | |

## Schedule sources

Gyms or studios to pull real class times from. Feeds the anchoring rule — a
standing priority prefers a slot that lands on a real class.

`site` is the Virtuagym subdomain and `club` the `pref_club` id; both are
visible in any schedule URL. `categories` maps a label you choose to the
`event_type` id of each schedule tab the gym publishes.

- site: <subdomain>
  club: <pref_club id>
  categories: <label>=<event_type>, <label>=<event_type>
  feeds: <standing priority name>

<!-- optional; leave empty and only the hand-written anchors below are used -->

## Anchored options

Hand-entered scheduled things a priority can attach to — a standing group run,
a lesson slot. A block that maps to something real in the world gets done;
a floating "45m exercise" doesn't.

For gym classes, prefer **Schedule sources** above — those are fetched fresh, so
they don't go stale the way a hand-written list does.

Format: `Day HH:MM–HH:MM · Name`

<!-- optional; leave empty and the skill slots into any qualifying gap -->
