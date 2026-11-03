# standup config

Copy to `~/.local/ai/standup/config.md` and fill in. Hand-edited. The skill reads
this every run and never writes to it. **All account-specific values live here**,
so the skill itself stays free of personal data.

A symlink is fine if you keep config somewhere else (a private repo, say): the
skill only needs this path to resolve.

## Paths

- `run_log`: `~/.local/ai/standup/log.md`. The skill appends one line per emitted
  standup and reads the last line to start the next window.

## Window

- `timezone`: America/New_York
- `working_days`: Mon, Tue, Wed, Thu, Fri
- `max_lookback_days`: 4. If the last run is older than this (vacation, a
  missed week), the window falls back to the previous working day instead of
  dumping two weeks of work into one standup.

## Calendar

Calendar **IDs**, not display names. Get them from `list_calendars` once during
setup. List only calendars that hold work meetings. A family or personal
calendar here puts school pickups in your standup.

One line per calendar: `<id>`: `<type>`, a label. The type is `google` (the
default) or `feed`.

- `you@work.example.com`: google, work

**`google`** is a calendar you own or that's shared to you. Meetings are kept only
if they're public: drop events marked `private`, focus time, out-of-office,
working-location, all-day events, events marked free (transparent), events you
declined or never answered, and events with fewer than two other attendees (1:1s
and solo holds).

**`feed`** is an ICS feed imported into Google. An Outlook calendar published by URL
shows up as `<random>@import.calendar.google.com`; copy the id from the embed link's
`src=` (decode `%40` to `@`). A feed has no attendees or response status, so the
skill can't tell a 1:1 or a declined meeting by itself. It keeps timed, busy events
whose titles aren't privacy placeholders (`Busy`, `Private appointment`, ...) or
matches for the patterns below. In Outlook, publish the calendar with **Can view
all details** or every title arrives as `Busy`.

- `exclude_titles`: titles (case-insensitive substrings) to drop even when the
  rules above would keep them. For example `lunch`, `hold`, `interview`.
- `one_on_one_patterns`: title substrings that mark a 1:1 on a feed calendar,
  where attendee counts aren't available. For example `1:1`, `<>`, `1-on-1`.

## GitHub

`gh` covers every repo you can see; no repo list needed. Narrow it if a
personal or open-source repo shouldn't show up at work:

- `exclude_repos`: (none). `owner/name` entries to drop.

## Issue tracker

- `data_source`: `collection://<uuid>`. From `notion-fetch` on the database.
- `assignee_id`: `<notion user id>`. From `notion-get-users` with
  `user_id: "self"`, looked up once and stored here so the daily run skips the call.
  A person property serializes as a JSON array of `user://<id>` strings, so the
  skill matches it with `LIKE '%<id>%'`.
- `assignee_column`: `Assignee`. The person property that says whose ticket it is.
- `ticket_id_prefix`: `STH`. The prefix in PR titles and branch names that ties a
  PR to a ticket (`STH-1234`). Its numeric part matches the `Task ID` column.
- `id_column`: `Task ID`
- `title_column`: `Task name`
- `status_column`: `Status`
- `shipped_statuses`: `Released`, `Completed`
- `doing_statuses`: `In progress`, `In review`

## Slack

**Public channels only by default.** The search runs through the public-only
Slack tool, so private channels, DMs and group DMs never reach a standup unless
you list a channel below.

- `include_channels`: (none). Private channels whose long posts may count anyway,
  by name (`#eng-private`). DMs and group DMs can't be included.
- `exclude_channels`: (none). Public channels to skip, such as social channels
  or anything with sensitive discussions.
- `min_chars`: 280. A single post counts when it's at least this long.
- `min_thread_messages`: 3. A thread counts when you posted at least this many
  messages in it during the window, even if each one is short.

## Work log (optional)

A channel where you post a running log with a tag per line, such as
`[eng] shipped X` or `[exec] leadership meeting`. Each tagged line is a "Did"
candidate. Posts here are read even if the channel is private, because you
named it here.

- `work_log_channel`: `#your-work-log`
- `work_log_skip_tags`: `in`, `out`. Clock-in and clock-out markers, never bullets.

<!-- optional; delete the section or leave the channel empty if you have no log -->

## Hub (optional)

Hub files from the `hub` plugin, read for work in flight. The current repo's
`.local/ai/hub/hub.md` is always checked; list others here so the standup sees
them from any directory.

- `hub_files`: (none). Absolute paths to `hub.md` files.

## Output

- `link_style`: `markdown`. Choices are `markdown` (`[STH-12](url)`) or `bare`
  (`STH-12 url`). Check once by pasting a standup into Slack: if the brackets show
  up literally instead of as links, set `bare`.
