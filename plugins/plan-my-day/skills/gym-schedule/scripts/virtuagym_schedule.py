#!/usr/bin/env python3
"""Read class schedules from Virtuagym-hosted gyms.

Standard library only. See SKILL.md for why the odd bits are the way they are.
"""

import datetime
import re
from html.parser import HTMLParser
from typing import Dict, FrozenSet, List, NamedTuple, Optional, Tuple

_TIME_RE = re.compile(
    r"^\s*(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*-\s*(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*$",
    re.IGNORECASE,
)

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
