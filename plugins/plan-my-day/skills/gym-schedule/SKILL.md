---
name: gym-schedule
description: Look up class and pool schedules at a Virtuagym-hosted gym — what's on tonight, when a lap swim lane is open this week, which classes fit a gap. Use whenever the user asks about gym classes, swim times, or fitting exercise into a day.
---

# Gym Schedule

Reads a gym's published class grid so an exercise block can be anchored to a
real class time. A block that maps to something scheduled in the world gets
done; a floating "45m exercise" doesn't.

## Running it

`scripts/virtuagym_schedule.py --help` has the flags. Read it rather than
guessing — it is the source of truth for the interface.

Site, club, and category ids come from the **Schedule sources** section of
`~/.local/ai/agenda/config.md`. Read that file first. The script never reads it;
you construct the invocation.

If no config exists, ask for the gym's Virtuagym subdomain and club id rather
than guessing. Both are visible in any schedule URL:
`https://<subdomain>.virtuagym.com/classes/week/<date>?event_type=<id>&…&pref_club=<club>`.
The `event_type` values are the categories — one per schedule tab the gym
publishes, and they differ per gym.

## The two shapes of question

**"What's on tonight?"** — today's date, plus `--after` to bound it to the
evening. Cross the result against the calendar before suggesting anything.

**"When could I fit a swim in this week?"** — widen `--days`, then look for
sessions that land in calendar gaps. Widening within one week costs nothing:
the fetch is a whole week regardless, so filtering is free.

## What the output will not tell you

**`past_per_server` is the gym's clock, not yours.** It reflects when the page
was generated. Never use it to decide something has already happened — compare
the start time against the real current time.

**Concurrent entries are real, not duplicates.** Two pool programs commonly
share a slot ("Lap Swim (5 Lanes)" and "Water Walking" both at 06:30–07:25),
and lane counts vary hour to hour. Never collapse rows that share a time.

**Times are local to the gym and never converted.** If the user is in a
different timezone than the gym, say so rather than quietly doing the math.

**Nothing here is a booking.** The script reads a schedule. It cannot reserve a
spot, and a listed class may still be full.

## Reading the footer

Output ends with a per-category count: `— pool 12 · group 9`. A zero there means
that category contributed nothing *after filtering* — often legitimate, as in
`--after 17:00` on a day with no evening lap swim.

A category that returned nothing **at all** is different: the script writes a
warning to stderr naming it. That usually means a wrong `event_type` id, not a
quiet day. Repeat it rather than planning around a schedule you only half have.

If the script exits non-zero, report it and move on. Do not fall back to
fetching the page yourself: a non-zero exit means no category parsed any rows,
which is the signature of changed markup, and guessing at it produces a
plausible-looking wrong schedule.
