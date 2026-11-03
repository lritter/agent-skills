---
name: standup
description: Daily standup writer. Reads calendar, GitHub, the issue tracker, public Slack, and optionally a work-log channel and the hub, drafts a Did/Doing list since the last standup, asks one round of questions, then prints the list ready to paste into Slack. Run manually.
disable-model-invocation: true
argument-hint: "[what you plan to work on today]"
---

# Standup

Write **one standup**: a short "Did" and "Doing" list, every bullet one line, every
ticket and PR a link the reader can click. The result is pasted into Slack, so it's
printed, not posted.

```
Did:
- Shipped [ABC-101](https://…) Export endpoint streams CSV
- Reviewed [api#40](https://…) Rate limiter for public API (sam)
- Q4 planning
- Discussed export pagination in #eng ([thread](https://…))
Doing:
- [ABC-103](https://…) Paginate export — in review ([api#45](https://…))
- 14:00 Incident retro
- Write the importer runbook
```

## The contract

Three phases, one checkpoint. A standup that turns into a conversation has failed.

1. **Gather**: read every source in parallel, in one wave. Ask nothing.
2. **Checkpoint**: one message with the drafted list and two questions.
3. **Emit**: the final list, then one line appended to the run log.

Go back for a second round only if an answer can't be applied without one (it names
a ticket you can't find, say). On a third exchange, stop and emit with the gap noted
under the list.

**Arguments.** Text after the command is the answer to "what are you working on
today?". Fold it into Doing and drop that question from the checkpoint; still ask
whether anything should change.

## Config

Read `~/.local/ai/standup/config.md` first. Everything account-specific is there:
calendar ids, the tracker's data source and your assignee id, Slack scope, the work
log channel, hub files. **Never put any of those values in this skill.**

If the file is missing, copy `reference/config.template.md` into place and walk the
user through filling it in. That's the whole first run; don't write a standup
against a template. Placeholders in angle brackets count as unset: a section that
still holds them is a source that's **not configured**, reported as such.

## The window

"Did" covers **since the last standup**.

1. Find now in the config's timezone (`date`, or the session's date if Bash can't
   run).
2. Read the run log's last line. If it's there and no more than `max_lookback_days`
   old, the window starts at its timestamp.
3. Otherwise the window starts at 00:00 on the previous working day: Friday when
   today is Monday, yesterday otherwise (skipping non-working days per config).

Say which rule applied in the checkpoint's first line ("Since your last standup,
Fri 09:40" or "Since Friday (no run logged)").

"Doing" covers the rest of **today**, from now until end of day.

## Phase 1: Gather

Load every deferred tool in **one** `ToolSearch` call. MCP prefixes differ between
installs, so search by the suffix: `list_events`, `notion-query-data-sources`,
`slack_search_public`, `slack_search_public_and_private`.

Then issue every read in a single block so they run concurrently.

| Source | How |
| --- | --- |
| Config + run log | `Read` both |
| Calendar (window) | `list_events` per configured calendar id, window start → now |
| Calendar (today) | `list_events` per calendar id, now → end of today |
| Merged PRs | `gh search prs --author=@me --merged-at=">=<window date>" --json repository,number,title,url,closedAt --limit 50` |
| Opened PRs | `gh search prs --author=@me --created=">=<window date>" --json repository,number,title,url,state,isDraft --limit 50` |
| Your open PRs | `gh search prs --author=@me --state=open --json repository,number,title,url,isDraft,updatedAt --limit 50` |
| Reviewed PRs | `gh search prs --reviewed-by=@me --updated=">=<window date>" --json repository,number,title,url,author --limit 30 -- -author:@me` |
| Commented PRs | `gh search prs --commenter=@me --updated=">=<window date>" --json repository,number,title,url,author --limit 30 -- -author:@me` |
| Tickets | `notion-query-data-sources`, query below |
| Slack | `slack_search_public`, query below |
| Work log | `slack_search_public_and_private`, `in:<work_log_channel> from:me`, same `after`, if configured |
| Hub | `Read` `.local/ai/hub/hub.md` in the current repo and each `hub_files` entry; a missing file is fine |

`gh search` works from any directory and covers every repo you can see. Drop
`exclude_repos`.

### The queries that need to be exactly right

**Reviews.** `--reviewed-by` and `--commenter` match your own PRs too (any comment
on your own PR counts), so the trailing `-- -author:@me` isn't optional. They also
have no date filter of their own: `--updated` matches a PR you reviewed last month
that someone touched today. For each candidate, check that a review or comment of
yours falls inside the window (`gh pr view <url> --json reviews,comments`, filter on
your login and `submittedAt`/`createdAt`). Drop the ones without one. If that
check can't run, keep the candidates and mark them `(review date unverified)` in
the draft.

**Tickets.** Filter on the assignee, never on status alone (a shared backlog's
statuses are mostly other people's work). The person property serializes as a JSON
array of `user://<id>` strings:

```sql
SELECT url, "<id_column>", "<title_column>", "<status_column>"
FROM "<data_source>"
WHERE "<assignee_column>" LIKE '%<assignee_id>%'
  AND "<status_column>" IN (<shipped_statuses>, <doing_statuses>)
ORDER BY "<id_column>" DESC
```

The data source has **no status-change timestamp**, so "Released" alone can't tell
you whether a ticket shipped this window or last quarter. A ticket counts as
**shipped** only when it's in a shipped status **and** a PR that merged in the window
carries its id (`<ticket_id_prefix>-<n>` in the PR title). Released tickets with no
merged PR in the window stay out. If a ticket shipped without a PR (a doc, an ops
change), the user adds it at the checkpoint.

**Slack.** Public channels only, through `slack_search_public`:

```
query: from:me    after: <window start as a Unix timestamp>    sort: timestamp
include_context: false
```

Use the `after` **parameter** (a Unix timestamp, inclusive), not the `after:` query
modifier, which takes a date and is exclusive. Page with `cursor` until the results
run out.

The public-and-private tool is used only with an explicit `in:<channel>` for each
`include_channels` entry and for the work log, both named in config, which is the
user's consent for those channels. **Never search DMs or group DMs**, and never run
the public-and-private tool without an `in:` restriction. Drop `exclude_channels`.

Keep only:
- a single post of at least `min_chars` characters, or
- a thread where you posted at least `min_thread_messages` times in the window
  (group by the `thread_ts` in each permalink).

Skip one-liners, link-only posts, and reactions. One bullet per thread, not per
message, naming the topic and the channel and linking the permalink.

**Work log.** Each line with a tag (`[eng] …`, `[exec] …`) is a Did candidate in your
own words. Skip `work_log_skip_tags`. These often name meetings the calendar can't
see; keep the log's wording and drop any duplicate of a calendar bullet.

### Calendar: what counts as public

Keep an event only if **all** hold:
- `visibility` isn't `private` or `confidential`;
- `eventType` is `DEFAULT` (not focus time, out-of-office, working location);
- it has a start time (not all-day) and isn't marked free (`transparency: transparent`);
- your attendee entry (`self: true`) has `responseStatus: accepted` (you organized it,
  or accepted). `needsAction`, `tentative` and `declined` are out;
- it has **at least two other attendees** (1:1s and solo holds are out);
- its title doesn't match `exclude_titles`.

Use the event's own title. Don't add attendees, descriptions, or meeting notes. A
title can carry details that only make sense in a calendar; trim it to what the
meeting is.

If every configured calendar returns zero kept events across both window and today,
say so in the checkpoint ("Calendar: 0 public meetings, is the configured calendar
your work one?"). That's usually a personal calendar in config, not a quiet week.

### Degrade loudly

A source that fails or isn't configured gets one line under the draft:

```
Slack: NOT CHECKED — MCP auth expired, re-auth with /mcp
GitHub: NOT CHECKED — gh couldn't run here
Work log: not configured
```

Never omit a source silently. A standup that's missing yesterday's merge is worse
than one that says it couldn't look.

## Building the draft

**Did** (in this order):
1. **Shipped**: one bullet per shipped ticket, with the ticket link and its title. If
   the merged PR adds something the title doesn't, append `([#652](pr url))`.
2. **Merged** PRs with no shipped ticket: `Merged [repo#n](url) <title>`. A PR whose
   ticket is still In review or In progress is merged, not shipped.
3. **Opened** PRs not merged yet: `Opened [repo#n](url) <title>`.
4. **Reviews**: `Reviewed [repo#n](url) <title> (<author login>)`. A PR you only
   commented on reads `Commented on`.
5. **Meetings**: the calendar title, plus work-log lines naming meetings.
6. **Slack**: `Discussed <topic> in #channel ([thread](permalink))`.
7. Remaining work-log lines.

**Doing**:
1. Tickets **In review**, linking the open PR if there is one.
2. Tickets **In progress** that are clearly active: an open PR, a hub session, or a
   Did bullet in this window. Other In progress tickets go in a short "also
   assigned, not in the draft" line at the checkpoint, so stale ones don't pad the
   list but the user can pull one in.
3. Open PRs of yours with no ticket, if updated in the window. A draft nobody has
   touched since last month isn't today's work.
4. The rest of today's public meetings, with start time: `14:00 Eng sync`.
5. The user's answer about today's plans.

**Rules for every bullet:**
- One line. Cut the title before wrapping. No sub-bullets.
- Every ticket and PR is a link, in the configured `link_style`. Ticket links use the
  `url` the query returned; PR links use `gh`'s `url`.
- One bullet per piece of work. A ticket, its PR and its review thread are one bullet.
- Strip the `<ticket_id_prefix>-<n>:` prefix from PR titles. When a PR has a ticket,
  link the ticket in the same bullet instead of repeating its id as plain text.
- Hub text is for spotting work in flight, not for copying: its lines are written for
  the hub's own operator. Use the ticket title instead.

## Phase 2: The checkpoint

One message, in this order:

1. The window line.
2. The draft, in a fenced block.
3. The source lines (`NOT CHECKED`, `not configured`, unverified review dates).
4. "Also assigned, not in the draft", if any.
5. The questions, through `AskUserQuestion` if available, otherwise as plain text:
   - **What are you planning to work on today?** (Skip if the arguments answered it.)
   - **Anything to add, drop, or reword?**

Then stop and wait. Don't emit the final list in the same message.

## Phase 3: Emit

1. Apply the changes. Fold the plans answer into Doing as one-line bullets, in the
   user's words, tightened. Link a ticket they name if the query returned it.
2. Append to the run log:
   ```
   | 2026-11-03T09:42-05:00 | emitted |
   ```
   ISO timestamp with offset, one line, unpadded. Create the file with a
   `# standup run log` heading if it's missing. Only Emit writes it. A checkpoint
   that never got an answer isn't a standup, and logging it would shrink tomorrow's
   window. If the write fails, say so in one line under the list.
3. Print the final list **inside a fenced code block** (` ```text `), as the last
   thing in your reply, with nothing after it but that one failure line if there is
   one. Rendered Markdown in a terminal hides the link targets, and copying it drops
   them. The raw text in a code block pastes into Slack with the links intact.

Don't post anywhere. If the user asks for it to go to Slack, draft it with the Slack
tool's draft function for them to send, and name the channel first.
