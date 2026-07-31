#!/usr/bin/env python3
"""Read class schedules from Virtuagym-hosted gyms.

Standard library only. See SKILL.md for why the odd bits are the way they are.
"""

import argparse
import datetime
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from typing import Dict, FrozenSet, Iterable, List, NamedTuple, Optional, Sequence, Tuple

_TIME_RE = re.compile(
    r"^\s*(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*-\s*(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*$",
    re.IGNORECASE,
)


def _to_24h(hour: str, minute: str, meridiem: str) -> str:
    h = int(hour) % 12          # 12 am -> 0, 12 pm -> 0 before the += 12 below
    if meridiem.lower() == "p":
        h += 12
    return "%02d:%s" % (h, minute)


def parse_time_range(text: str) -> Tuple[str, str]:
    """'06:30 am - 07:25 am' -> ('06:30', '07:25'). Raises ValueError if malformed."""
    match = _TIME_RE.match(text)
    if not match:
        raise ValueError("unparseable time range: %r" % (text,))
    start = _to_24h(match.group(1), match.group(2), match.group(3))
    end = _to_24h(match.group(4), match.group(5), match.group(6))
    return start, end


_CLOCK_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

_DAY_CLASS_PREFIX = "internal-event-day-"
_MODAL_RE = re.compile(r"openScheduleModal\('([^']+)'\)")
_FIELDS = ("classname", "time", "instructor")
# Hardcoded rather than strftime("%A"): that is locale-dependent, and a French
# locale would silently emit "lundi" into output plan-my-day reads.
_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday")


class Session(NamedTuple):
    date: str
    weekday: str
    start: str
    end: str
    name: str
    instructor: Optional[str]
    category: str
    past_per_server: bool
    detail_url: Optional[str]


class ParsedWeek(NamedTuple):
    sessions: List[Session]
    dates: FrozenSet[str]


class _GridParser(HTMLParser):
    """Collect every div carrying an internal-event-day-* class.

    Spacer cells carry the day class too, with empty name and time. They are
    kept here because they are how the page's date coverage is known; parse_week
    drops them from sessions.
    """

    def __init__(self) -> None:
        HTMLParser.__init__(self, convert_charrefs=True)
        self.cells = []  # type: List[Dict[str, object]]
        self._cell = None  # type: Optional[Dict[str, object]]
        self._depth = 0
        self._field = None  # type: Optional[str]

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag == "div" and self._cell is None:
            day = None
            for name in classes:
                if name.startswith(_DAY_CLASS_PREFIX):
                    day = name[len(_DAY_CLASS_PREFIX):]
                    break
            if day is not None:
                self._cell = {
                    "day": day,
                    "past": "class_past" in classes,
                    "onclick": attributes.get("onclick") or "",
                    "classname": "",
                    "time": "",
                    "instructor": "",
                }
                self._depth = 1
                return
        if self._cell is None:
            return
        if tag == "div":
            self._depth += 1
        elif tag == "span":
            for field in _FIELDS:
                if field in classes:
                    self._field = field

    def handle_endtag(self, tag):
        if self._cell is None:
            return
        if tag == "span":
            self._field = None
        elif tag == "div":
            self._depth -= 1
            if self._depth == 0:
                self.cells.append(self._cell)
                self._cell = None

    def handle_data(self, data):
        if self._cell is not None and self._field is not None:
            self._cell[self._field] += data


def _collapse(text: str) -> str:
    """Trim and squeeze internal runs of whitespace to one space."""
    return " ".join(text.split())


def _iso_date(day_token: str) -> str:
    """'27-07-2026' -> '2026-07-27'. Day-month-year; validated, not just reordered."""
    parts = day_token.split("-")
    if len(parts) != 3:
        raise ValueError("unexpected day token: %r" % (day_token,))
    day, month, year = parts
    return datetime.date(int(year), int(month), int(day)).isoformat()


def _weekday_name(iso: str) -> str:
    parsed = datetime.date(*[int(part) for part in iso.split("-")])
    return _WEEKDAYS[parsed.weekday()]


def parse_week(html: str, category: str, base_url: str) -> ParsedWeek:
    """Parse one Virtuagym week page into sessions plus the dates it covered."""
    parser = _GridParser()
    parser.feed(html)
    parser.close()

    sessions = []  # type: List[Session]
    dates = set()
    for cell in parser.cells:
        iso = _iso_date(str(cell["day"]))
        dates.add(iso)

        name = _collapse(str(cell["classname"]))
        time_text = _collapse(str(cell["time"]))
        if not name or not time_text:
            continue  # layout spacer, not a class

        start, end = parse_time_range(time_text)
        instructor = _collapse(str(cell["instructor"])) or None

        detail_url = None
        modal = _MODAL_RE.search(str(cell["onclick"]))
        if modal:
            detail_url = base_url.rstrip("/") + modal.group(1)

        sessions.append(Session(
            date=iso,
            weekday=_weekday_name(iso),
            start=start,
            end=end,
            name=name,
            instructor=instructor,
            category=category,
            past_per_server=bool(cell["past"]),
            detail_url=detail_url,
        ))

    return ParsedWeek(sessions=sessions, dates=frozenset(dates))


def filter_sessions(
    sessions,             # type: Sequence[Session]
    dates,                # type: Iterable[str]
    after=None,           # type: Optional[str]
    before=None,          # type: Optional[str]
    match=None,           # type: Optional[str]
):
    # type: (...) -> List[Session]
    """Filter by ISO date, start-time window, and a case-insensitive name regex.

    `after` is inclusive, `before` exclusive, and both compare against the start
    time -- a class that runs past `before` is still kept, because the question
    is when you can show up.
    """
    wanted = set(dates)
    pattern = re.compile(match, re.IGNORECASE) if match else None

    kept = []
    for session in sessions:
        if session.date not in wanted:
            continue
        if after is not None and session.start < after:
            continue
        if before is not None and session.start >= before:
            continue
        if pattern is not None and not pattern.search(session.name):
            continue
        kept.append(session)

    kept.sort(key=lambda s: (s.date, s.start, s.category, s.name))
    return kept


_URL_TEMPLATE = (
    "https://{host}/classes/week/{anchor}"
    "?event_type={event_type}&coach=0&activity_id=0&member_id_filter=0"
    "&embedded=1&planner_type=1&show_personnel_schedule="
    "&in_app=0&single_club=0&pref_club={club}"
)
_USER_AGENT = "gym-schedule (Claude Code skill; stdlib urllib)"
_MAX_DAYS = 62


class ScheduleError(Exception):
    """Anything that means the caller must not treat the result as a schedule."""


def resolve_host(site: str) -> str:
    """'example-gym' -> 'example-gym.virtuagym.com'. A full hostname passes through."""
    return site if "." in site else site + ".virtuagym.com"


def week_url(host: str, club: str, event_type: str, anchor_date: str) -> str:
    return _URL_TEMPLATE.format(
        host=host, anchor=anchor_date, event_type=event_type, club=club)


def date_range(start: str, days: int) -> List[str]:
    if days < 1:
        raise ValueError("--days must be at least 1, got %r" % (days,))
    if days > _MAX_DAYS:
        # Each uncovered week is another request to the gym. Claude builds
        # this invocation, so cap the blast radius rather than trusting it.
        raise ValueError("--days must be at most %d, got %r" % (_MAX_DAYS, days))
    try:
        first = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError("--date expects an ISO date (YYYY-MM-DD), got %r" % (start,))
    return [(first + datetime.timedelta(days=n)).isoformat() for n in range(days)]


def http_fetch(url: str) -> str:
    """The real network call. Injected, so tests never reach it."""
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def collect(host, club, categories, dates, fetch):
    # type: (str, str, Sequence, Iterable[str], object) -> tuple
    """Fetch every week page needed to cover `dates`, for every category.

    Deduplicates by the dates a page actually covered, so no week-start
    convention is assumed. Returns (all sessions, pre-filter count per label,
    uncovered dates per label).
    """
    wanted = sorted(set(dates))
    sessions = []  # type: List[Session]
    counts = {}  # type: Dict[str, int]
    uncovered = {}  # type: Dict[str, List[str]]
    base_url = "https://" + host

    for label, event_type in categories:
        counts[label] = 0
        uncovered[label] = []
        covered = set()  # type: set
        outstanding = list(wanted)

        while outstanding:
            anchor = outstanding[0]
            url = week_url(host, club, event_type, anchor)
            try:
                html = fetch(url)
            except ScheduleError:
                raise
            except Exception as error:
                raise ScheduleError("fetch failed for %s: %s" % (url, error))

            try:
                parsed = parse_week(html, label, base_url)
            except ValueError as error:
                # An unparseable time or day token means the markup drifted.
                # That must degrade to one clean line, not a traceback -- it is
                # the most likely drift and the whole reason ScheduleError exists.
                raise ScheduleError(
                    "could not parse the %s page for %s: %s" % (label, anchor, error))

            if not parsed.dates:
                # No day cells at all. On the first pass this means the category
                # is dead (usually a wrong event_type id). Later it means a week
                # we cannot cover. Either way stop asking; record what is left so
                # main() can say so rather than silently returning partial data.
                uncovered[label] = list(outstanding)
                break
            if anchor not in parsed.dates:
                # Day cells exist but not the one requested: the markup or URL
                # scheme changed. Without this guard the loop never terminates.
                raise ScheduleError(
                    "page for %s did not cover that date (covered: %s) -- the "
                    "markup or URL scheme has probably changed"
                    % (anchor, ", ".join(sorted(parsed.dates)))
                )

            sessions.extend(parsed.sessions)
            counts[label] += len(parsed.sessions)
            covered |= set(parsed.dates)
            outstanding = [d for d in outstanding if d not in covered]

    return sessions, counts, uncovered


def format_text(sessions, counts):
    # type: (Sequence[Session], Dict[str, int]) -> str
    """Human- and Claude-readable listing, grouped by day, with a count footer."""
    lines = []
    if not sessions:
        lines.append("No sessions matched.")
    else:
        width = max(len(label) for label in counts) if counts else 0
        current_date = None
        for session in sessions:
            if session.date != current_date:
                if current_date is not None:
                    lines.append("")
                lines.append("%s %s" % (session.date, session.weekday))
                current_date = session.date
            row = "  %s–%s  %s  %s" % (
                session.start, session.end, session.category.ljust(width), session.name)
            if session.instructor:
                row += " — " + session.instructor
            lines.append(row)

    footer = " · ".join(
        "%s %d" % (label, counts[label]) for label in sorted(counts))
    lines.append("")
    lines.append("— " + footer)
    return "\n".join(lines)


def format_json(host, club, dates, sessions, counts):
    # type: (str, str, Sequence[str], Sequence[Session], Dict[str, int]) -> str
    payload = {
        "site": host,
        "club": club,
        "dates": list(dates),
        "counts": counts,
        "sessions": [session._asdict() for session in sessions],
    }
    return json.dumps(payload, indent=2, sort_keys=False)


def parse_category(value: str) -> Tuple[str, str]:
    """'pool=1204' -> ('pool', '1204')."""
    if "=" not in value:
        raise ValueError("expected LABEL=EVENT_TYPE, got %r" % (value,))
    label, event_type = value.split("=", 1)
    label, event_type = label.strip(), event_type.strip()
    if not label or not event_type:
        raise ValueError("expected LABEL=EVENT_TYPE, got %r" % (value,))
    return label, event_type


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="virtuagym_schedule.py",
        description="Read class schedules from a Virtuagym-hosted gym.",
        epilog=(
            "The page fetched is always a whole week, so widening --days within "
            "one week costs no extra requests. Times are local to the gym and "
            "are never converted."
        ),
    )
    parser.add_argument("--site", required=True,
                        help="Virtuagym subdomain (e.g. example-gym) or full hostname")
    parser.add_argument("--club", required=True, help="pref_club id from the schedule URL")
    parser.add_argument("--category", action="append", required=True,
                        metavar="LABEL=EVENT_TYPE",
                        help="repeatable, e.g. --category pool=1204 --category group=1203")
    parser.add_argument("--date", default=None,
                        help="ISO start date; defaults to today")
    parser.add_argument("--days", type=int, default=1,
                        help="number of days from --date, inclusive (default 1)")
    parser.add_argument("--after", default=None,
                        help="keep classes starting at or after HH:MM")
    parser.add_argument("--before", default=None,
                        help="keep classes starting strictly before HH:MM")
    parser.add_argument("--match", default=None,
                        help="case-insensitive regex against the class name")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv=None, fetch=http_fetch, stdout=None, stderr=None):
    # type: (Optional[Sequence[str]], object, object, object) -> int
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        categories = [parse_category(value) for value in args.category]
    except ValueError as error:
        parser.error(str(error))  # exits 2

    seen = set()
    for label, _event_type in categories:
        if label in seen:
            parser.error("duplicate --category label %r" % (label,))
        seen.add(label)

    # Reject malformed clock times rather than string-comparing them. "9:00"
    # sorts after "10:00", so an unvalidated window silently returns the wrong
    # rows -- exactly the plausible-looking wrong answer this tool exists to
    # avoid. Callers construct these programmatically, so loud is right.
    for flag, value in (("--after", args.after), ("--before", args.before)):
        if value is not None and not _CLOCK_RE.match(value):
            parser.error(
                "%s expects a 24-hour HH:MM time (e.g. 17:00), got %r" % (flag, value))

    if args.match is not None:
        try:
            re.compile(args.match)
        except re.error as error:
            parser.error("--match is not a valid regex: %s" % (error,))

    start = args.date or datetime.date.today().isoformat()
    try:
        dates = date_range(start, args.days)
    except ValueError as error:
        parser.error(str(error))  # exits 2

    host = resolve_host(args.site)

    try:
        sessions, counts, uncovered = collect(
            host, args.club, categories, dates, fetch)
    except ScheduleError as error:
        stderr.write("gym-schedule: %s\n" % (error,))
        return 1

    if not any(counts.values()):
        stderr.write(
            "gym-schedule: no rows parsed for any category (%s) -- treating as a "
            "failure, not an empty schedule. The markup or ids may have changed.\n"
            % ", ".join("%s=%s" % pair for pair in categories)
        )
        return 1

    for label, _event_type in categories:
        if counts[label] == 0:
            stderr.write(
                "gym-schedule: warning: category %r returned no rows at all; "
                "check its event_type id.\n" % (label,)
            )
        elif uncovered.get(label):
            # Partial coverage: some rows came back, but a later week did not.
            # Returning 7 days when 14 were asked for, silently, is worse than
            # saying so.
            stderr.write(
                "gym-schedule: warning: category %r returned no schedule for %s; "
                "those dates are missing from the results.\n"
                % (label, ", ".join(uncovered[label]))
            )

    # A wrong event_type is not an error to this server: it falls back to a
    # default schedule and returns 200. Measured on one real club, event_type
    # 9999 and "abc" both returned byte-identical rows to a valid id. Nothing in
    # a single response can reveal that -- but two categories that come back
    # identical are a reliable tell, and cost nothing to check.
    signatures = {}  # type: Dict[str, frozenset]
    for label, _event_type in categories:
        signatures[label] = frozenset(
            (s.date, s.start, s.name) for s in sessions if s.category == label)
    labels = [label for label, _ in categories]
    for i, left in enumerate(labels):
        for right in labels[i + 1:]:
            if signatures[left] and signatures[left] == signatures[right]:
                stderr.write(
                    "gym-schedule: warning: categories %r and %r returned "
                    "identical schedules; at least one event_type id is probably "
                    "wrong (this server serves a default schedule for unknown "
                    "ids rather than failing).\n" % (left, right)
                )

    kept = filter_sessions(sessions, dates, args.after, args.before, args.match)
    displayed = dict((label, 0) for label, _ in categories)
    for session in kept:
        displayed[session.category] += 1

    if args.format == "json":
        stdout.write(format_json(host, args.club, dates, kept, displayed) + "\n")
    else:
        stdout.write(format_text(kept, displayed) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
