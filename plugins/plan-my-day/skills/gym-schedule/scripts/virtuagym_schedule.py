#!/usr/bin/env python3
"""Read class schedules from Virtuagym-hosted gyms.

Standard library only. See SKILL.md for why the odd bits are the way they are.
"""

import re
from typing import Tuple

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
