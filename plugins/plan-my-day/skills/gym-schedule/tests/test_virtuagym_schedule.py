import io
import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from virtuagym_schedule import (
    ScheduleError, Session, collect, date_range, filter_sessions, format_json,
    format_text, main, parse_category, parse_time_range, parse_week, resolve_host,
    week_url,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
BASE = "https://example-gym.virtuagym.com"

POOL_PER_DAY = {
    "2026-07-27": 14, "2026-07-28": 15, "2026-07-29": 14, "2026-07-30": 14,
    "2026-07-31": 14, "2026-08-01": 7, "2026-08-02": 9,
}
GROUP_PER_DAY = {
    "2026-07-27": 16, "2026-07-28": 11, "2026-07-29": 12, "2026-07-30": 7,
    "2026-07-31": 8, "2026-08-01": 7, "2026-08-02": 6,
}


def load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as handle:
        return handle.read()


class TestParseTimeRange(unittest.TestCase):
    def test_morning_range(self):
        self.assertEqual(parse_time_range("06:30 am - 07:25 am"), ("06:30", "07:25"))

    def test_noon_stays_twelve(self):
        self.assertEqual(parse_time_range("12:00 pm - 12:45 pm"), ("12:00", "12:45"))

    def test_leading_zero_pm_hour(self):
        self.assertEqual(parse_time_range("12:00 pm - 01:45 pm"), ("12:00", "13:45"))

    def test_midnight_becomes_zero(self):
        self.assertEqual(parse_time_range("12:30 am - 01:00 am"), ("00:30", "01:00"))

    def test_surrounding_whitespace_tolerated(self):
        self.assertEqual(parse_time_range("\n  06:30 am - 07:25 am  "), ("06:30", "07:25"))

    def test_unparseable_raises(self):
        with self.assertRaises(ValueError):
            parse_time_range("all day")


class TestParseWeek(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = parse_week(load("week-2026-07-27-pool-1204.html"), "pool", BASE)
        cls.group = parse_week(load("week-2026-07-27-group-1203.html"), "group", BASE)

    def test_coverage_is_the_whole_week_including_empty_cells(self):
        self.assertEqual(sorted(self.pool.dates), sorted(POOL_PER_DAY))
        self.assertEqual(sorted(self.group.dates), sorted(GROUP_PER_DAY))

    def test_real_row_counts_per_day(self):
        for parsed, expected in ((self.pool, POOL_PER_DAY), (self.group, GROUP_PER_DAY)):
            actual = {}
            for session in parsed.sessions:
                actual[session.date] = actual.get(session.date, 0) + 1
            self.assertEqual(actual, expected)

    def test_spacer_cells_produce_no_rows(self):
        self.assertEqual(len(self.pool.sessions), 87)
        self.assertEqual(len(self.group.sessions), 67)
        for session in self.pool.sessions:
            self.assertTrue(session.name)
            self.assertTrue(session.start)

    def test_date_is_day_month_year_not_month_day(self):
        self.assertIn("2026-08-01", self.pool.dates)
        self.assertNotIn("2026-01-08", self.pool.dates)

    def test_weekday_name(self):
        first = [s for s in self.pool.sessions if s.date == "2026-07-27"][0]
        self.assertEqual(first.weekday, "Monday")

    def test_concurrent_sessions_are_not_deduped(self):
        at_0630 = [
            s for s in self.pool.sessions
            if s.date == "2026-07-27" and s.start == "06:30"
        ]
        self.assertEqual(
            sorted(s.name for s in at_0630),
            ["Lap Swim (5 Lanes)", "Water Walking"],
        )

    def test_pool_rows_have_no_instructor(self):
        first = [s for s in self.pool.sessions if s.date == "2026-07-27"][0]
        self.assertIsNone(first.instructor)

    def test_group_rows_carry_instructor(self):
        aerobics = [
            s for s in self.group.sessions
            if s.date == "2026-07-27" and s.name == "Water Aerobics"
        ][0]
        self.assertEqual(aerobics.instructor, "sharri mendez")
        self.assertEqual((aerobics.start, aerobics.end), ("07:30", "08:15"))

    def test_internal_whitespace_is_collapsed(self):
        names = set(s.name for s in self.group.sessions)
        self.assertIn("AOA Strength and Conditioning", names)

    def test_category_is_stamped_on_every_row(self):
        self.assertEqual(set(s.category for s in self.pool.sessions), {"pool"})
        self.assertEqual(set(s.category for s in self.group.sessions), {"group"})

    def test_past_flag_is_captured_not_applied(self):
        first = [s for s in self.pool.sessions if s.date == "2026-07-27"][0]
        self.assertTrue(first.past_per_server)

    def test_detail_url_is_absolute(self):
        first = [s for s in self.pool.sessions if s.date == "2026-07-27"][0]
        self.assertEqual(
            first.detail_url,
            BASE + "/classes/class/897257324-69694072ca91c9-00223726"
                   "?embedded=1&pref_club=42450",
        )

    def test_html_without_rows_yields_empty_parse(self):
        parsed = parse_week("<html><body><p>nope</p></body></html>", "pool", BASE)
        self.assertEqual(parsed.sessions, [])
        self.assertEqual(parsed.dates, frozenset())


class TestFilterSessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pool = parse_week(load("week-2026-07-27-pool-1204.html"), "pool", BASE)
        group = parse_week(load("week-2026-07-27-group-1203.html"), "group", BASE)
        cls.all = pool.sessions + group.sessions

    def test_single_date_selects_one_day_of_seven(self):
        kept = filter_sessions(self.all, ["2026-07-31"])
        self.assertEqual(set(s.date for s in kept), {"2026-07-31"})
        self.assertEqual(len(kept), 14 + 8)

    def test_multiple_dates(self):
        kept = filter_sessions(self.all, ["2026-08-01", "2026-08-02"])
        self.assertEqual(len(kept), 7 + 7 + 9 + 6)

    def test_after_is_inclusive_of_the_boundary(self):
        kept = filter_sessions(self.all, ["2026-07-27"], after="06:30")
        self.assertTrue(any(s.start == "06:30" for s in kept))
        self.assertTrue(all(s.start >= "06:30" for s in kept))

    def test_before_is_exclusive_of_the_boundary(self):
        kept = filter_sessions(self.all, ["2026-07-27"], before="06:30")
        self.assertTrue(all(s.start < "06:30" for s in kept))

    def test_before_filters_on_start_so_a_class_may_end_later(self):
        sessions = [Session("2026-07-27", "Monday", "20:30", "21:30", "Late Swim",
                            None, "pool", False, None)]
        self.assertEqual(len(filter_sessions(sessions, ["2026-07-27"], before="21:00")), 1)

    def test_match_is_case_insensitive_regex_on_name(self):
        kept = filter_sessions(self.all, ["2026-07-27"], match="lap swim")
        self.assertTrue(kept)
        self.assertTrue(all("lap swim" in s.name.lower() for s in kept))

    def test_match_alternation(self):
        kept = filter_sessions(self.all, ["2026-07-27"], match="water walking|water aerobics")
        self.assertEqual(
            sorted(set(s.name for s in kept)),
            ["Water Aerobics", "Water Walking"],
        )

    def test_results_are_sorted_by_date_then_start(self):
        kept = filter_sessions(self.all, ["2026-07-27", "2026-07-28"])
        keys = [(s.date, s.start) for s in kept]
        self.assertEqual(keys, sorted(keys))

    def test_no_match_returns_empty_not_error(self):
        self.assertEqual(filter_sessions(self.all, ["2026-07-27"], match="zumba on ice"), [])

    def test_unrequested_date_is_dropped(self):
        self.assertEqual(filter_sessions(self.all, ["2030-01-01"]), [])


def synthetic_week(days, name="Open Swim", time_text="09:00 am - 09:45 am"):
    """Minimal page covering `days` (DD-MM-YYYY), one real row and one spacer each."""
    cells = []
    for day in days:
        cells.append(
            '<div id="syn-%s" class="class class_available internal-event-day-%s">'
            '<div class="c_holder"><span class="classname">%s</span>'
            '<span class="time">%s</span>'
            '<span class="instructor"><i></i></span></div>'
            '<div id="syn-%s_p"></div></div>' % (day, day, name, time_text, day)
        )
        cells.append(
            '<div id="" class="class class_available internal-event-day-%s">'
            '<div class="c_holder"><span class="classname"></span>'
            '<span class="time"></span>'
            '<span class="instructor"><i></i></span></div>'
            '<div id="_p"></div></div>' % (day,)
        )
    return "<html><body><div id='schedule_content'>%s</div></body></html>" % "".join(cells)


AUGUST_WEEK_TWO = synthetic_week([
    "03-08-2026", "04-08-2026", "05-08-2026", "06-08-2026",
    "07-08-2026", "08-08-2026", "09-08-2026",
])


class _StubFetcher(object):
    """Serves the fixtures, records every URL, and can serve extra weeks by anchor."""

    def __init__(self, extra_weeks=None):
        self.urls = []
        self.extra = extra_weeks or {}

    def __call__(self, url):
        self.urls.append(url)
        anchor = re.search(r"/classes/week/(\d{4}-\d{2}-\d{2})", url)
        if anchor and anchor.group(1) in self.extra:
            return self.extra[anchor.group(1)]
        if "event_type=1204" in url:
            return load("week-2026-07-27-pool-1204.html")
        if "event_type=1203" in url:
            return load("week-2026-07-27-group-1203.html")
        return "<html></html>"


class TestFetchPlumbing(unittest.TestCase):
    def test_resolve_host_expands_a_bare_subdomain(self):
        self.assertEqual(resolve_host("example-gym"), "example-gym.virtuagym.com")

    def test_resolve_host_passes_through_a_full_host(self):
        self.assertEqual(resolve_host("gym.example.com"), "gym.example.com")

    def test_week_url_carries_event_type_and_club(self):
        url = week_url("example-gym.virtuagym.com", "00000", "1204", "2026-07-31")
        self.assertTrue(url.startswith(
            "https://example-gym.virtuagym.com/classes/week/2026-07-31?"))
        self.assertIn("event_type=1204", url)
        self.assertIn("pref_club=00000", url)
        self.assertIn("embedded=1", url)

    def test_date_range_is_inclusive_of_the_start(self):
        self.assertEqual(date_range("2026-07-31", 1), ["2026-07-31"])
        self.assertEqual(
            date_range("2026-07-31", 3),
            ["2026-07-31", "2026-08-01", "2026-08-02"],
        )

    def test_date_range_rejects_a_non_positive_span(self):
        with self.assertRaises(ValueError):
            date_range("2026-07-31", 0)


class TestCollect(unittest.TestCase):
    def test_one_fetch_per_category_for_dates_inside_one_week(self):
        fetch = _StubFetcher()
        sessions, counts = collect(
            "example-gym.virtuagym.com", "00000",
            [("pool", "1204"), ("group", "1203")],
            ["2026-07-27", "2026-07-31", "2026-08-02"],
            fetch,
        )
        self.assertEqual(len(fetch.urls), 2)
        self.assertEqual(counts, {"pool": 87, "group": 67})
        self.assertEqual(set(s.category for s in sessions), {"pool", "group"})

    def test_sessions_are_returned_unfiltered_for_the_whole_week(self):
        fetch = _StubFetcher()
        sessions, _ = collect(
            "example-gym.virtuagym.com", "00000", [("pool", "1204")],
            ["2026-07-31"], fetch,
        )
        self.assertEqual(len(sessions), 87)

    def test_a_span_crossing_a_week_boundary_fetches_each_week_once(self):
        # Sat/Sun fall in the fixture week; Mon 3 Aug is the next one.
        fetch = _StubFetcher({"2026-08-03": AUGUST_WEEK_TWO})
        sessions, counts = collect(
            "example-gym.virtuagym.com", "00000", [("pool", "1204")],
            ["2026-08-01", "2026-08-02", "2026-08-03"], fetch,
        )
        self.assertEqual(len(fetch.urls), 2)
        self.assertIn("/classes/week/2026-08-01", fetch.urls[0])
        self.assertIn("/classes/week/2026-08-03", fetch.urls[1])
        self.assertEqual(counts["pool"], 87 + 7)
        self.assertIn("2026-08-03", set(s.date for s in sessions))

    def test_a_category_returning_nothing_reports_zero_rather_than_failing(self):
        fetch = _StubFetcher()
        _, counts = collect(
            "example-gym.virtuagym.com", "00000",
            [("pool", "1204"), ("bogus", "9999")],
            ["2026-07-27"], fetch,
        )
        self.assertEqual(counts["bogus"], 0)
        self.assertEqual(counts["pool"], 87)

    def test_a_page_with_no_day_cells_at_all_is_a_dead_category_not_an_error(self):
        _, counts = collect(
            "h", "00000", [("dead", "9999")], ["2026-07-27"],
            lambda url: "<html><body></body></html>")
        self.assertEqual(counts, {"dead": 0})

    def test_a_page_covering_other_dates_but_not_the_requested_one_is_an_error(self):
        fetch = lambda url: load("week-2026-07-27-pool-1204.html")
        with self.assertRaises(ScheduleError):
            collect("h", "00000", [("pool", "1204")], ["2030-01-01"], fetch)

    def test_fetch_failure_becomes_a_schedule_error(self):
        def boom(url):
            raise IOError("connection refused")
        with self.assertRaises(ScheduleError):
            collect("h", "00000", [("pool", "1204")], ["2026-07-27"], boom)


SAMPLE = [
    Session("2026-07-31", "Friday", "06:30", "07:25", "Lap Swim (5 Lanes)",
            None, "pool", True, "https://x/1"),
    Session("2026-07-31", "Friday", "06:30", "07:25", "Water Walking",
            None, "pool", True, "https://x/2"),
    Session("2026-07-31", "Friday", "07:30", "08:15", "Water Aerobics",
            "sharri mendez", "group", True, "https://x/3"),
]


class TestFormatText(unittest.TestCase):
    def test_groups_by_day_with_a_heading(self):
        out = format_text(SAMPLE, {"pool": 2, "group": 1})
        self.assertIn("2026-07-31 Friday", out)

    def test_row_shows_times_name_and_category(self):
        out = format_text(SAMPLE, {"pool": 2, "group": 1})
        self.assertIn("06:30–07:25", out)
        self.assertIn("Lap Swim (5 Lanes)", out)
        self.assertIn("pool", out)

    def test_instructor_appended_when_present(self):
        out = format_text(SAMPLE, {"pool": 2, "group": 1})
        self.assertIn("Water Aerobics — sharri mendez", out)

    def test_no_trailing_dash_when_instructor_absent(self):
        out = format_text(SAMPLE, {"pool": 2, "group": 1})
        self.assertNotIn("Water Walking —", out)

    def test_footer_lists_every_category_count(self):
        out = format_text(SAMPLE, {"pool": 2, "group": 1})
        self.assertIn("pool 2", out)
        self.assertIn("group 1", out)

    def test_footer_shows_a_zero_category_rather_than_hiding_it(self):
        out = format_text(SAMPLE[:2], {"pool": 2, "group": 0})
        self.assertIn("group 0", out)

    def test_empty_result_says_so_and_still_prints_the_footer(self):
        out = format_text([], {"pool": 0, "group": 0})
        self.assertIn("No sessions matched", out)
        self.assertIn("pool 0", out)

    def test_two_days_get_two_headings(self):
        sessions = SAMPLE + [
            Session("2026-08-01", "Saturday", "09:00", "09:45", "Lap Swim (3 Lanes)",
                    None, "pool", False, None),
        ]
        out = format_text(sessions, {"pool": 3, "group": 1})
        self.assertIn("2026-07-31 Friday", out)
        self.assertIn("2026-08-01 Saturday", out)


class TestFormatJson(unittest.TestCase):
    def test_shape(self):
        payload = json.loads(format_json(
            "example-gym.virtuagym.com", "00000", ["2026-07-31"],
            SAMPLE, {"pool": 2, "group": 1}))
        self.assertEqual(payload["site"], "example-gym.virtuagym.com")
        self.assertEqual(payload["club"], "00000")
        self.assertEqual(payload["dates"], ["2026-07-31"])
        self.assertEqual(payload["counts"], {"pool": 2, "group": 1})
        self.assertEqual(len(payload["sessions"]), 3)

    def test_session_fields(self):
        payload = json.loads(format_json(
            "h", "00000", ["2026-07-31"], SAMPLE, {"pool": 2, "group": 1}))
        first = payload["sessions"][0]
        self.assertEqual(first["date"], "2026-07-31")
        self.assertEqual(first["weekday"], "Friday")
        self.assertEqual(first["start"], "06:30")
        self.assertEqual(first["end"], "07:25")
        self.assertEqual(first["name"], "Lap Swim (5 Lanes)")
        self.assertIsNone(first["instructor"])
        self.assertEqual(first["category"], "pool")
        self.assertTrue(first["past_per_server"])
        self.assertEqual(first["detail_url"], "https://x/1")

    def test_empty_result_is_valid_json_not_an_error(self):
        payload = json.loads(format_json("h", "00000", ["2026-07-31"], [], {"pool": 0}))
        self.assertEqual(payload["sessions"], [])
        self.assertEqual(payload["counts"], {"pool": 0})


class TestParseCategory(unittest.TestCase):
    def test_splits_label_from_event_type(self):
        self.assertEqual(parse_category("pool=1204"), ("pool", "1204"))

    def test_rejects_a_missing_equals(self):
        with self.assertRaises(ValueError):
            parse_category("pool")

    def test_rejects_an_empty_label(self):
        with self.assertRaises(ValueError):
            parse_category("=1204")


def run_main(args, fetch):
    out, err = io.StringIO(), io.StringIO()
    code = main(args, fetch=fetch, stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class TestMain(unittest.TestCase):
    def test_text_output_for_one_day(self):
        code, out, err = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--category", "group=1203",
             "--date", "2026-07-31"],
            _StubFetcher())
        self.assertEqual(code, 0)
        self.assertIn("2026-07-31 Friday", out)
        self.assertIn("pool 14", out)
        self.assertIn("group 8", out)
        self.assertNotIn("2026-07-30", out)

    def test_json_output_for_one_day(self):
        code, out, _ = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--date", "2026-07-31",
             "--format", "json"],
            _StubFetcher())
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["counts"], {"pool": 14})
        self.assertEqual(len(payload["sessions"]), 14)
        self.assertEqual(payload["site"], "example-gym.virtuagym.com")

    def test_days_span_inside_one_week_fetches_once_per_category(self):
        fetch = _StubFetcher()
        code, out, _ = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--date", "2026-07-27", "--days", "7"],
            fetch)
        self.assertEqual(code, 0)
        self.assertEqual(len(fetch.urls), 1)
        self.assertIn("pool 87", out)

    def test_time_window_and_match_compose(self):
        code, out, _ = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--date", "2026-07-27",
             "--after", "06:00", "--before", "07:00", "--match", "lap swim"],
            _StubFetcher())
        self.assertEqual(code, 0)
        self.assertIn("Lap Swim (5 Lanes)", out)
        self.assertNotIn("Water Walking", out)

    def test_filtered_to_nothing_is_success(self):
        code, out, _ = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--date", "2026-07-27",
             "--match", "zumba on ice"],
            _StubFetcher())
        self.assertEqual(code, 0)
        self.assertIn("No sessions matched", out)

    def test_one_dead_category_warns_but_succeeds(self):
        code, out, err = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--category", "bogus=9999",
             "--date", "2026-07-27"],
            _StubFetcher())
        self.assertEqual(code, 0)
        self.assertIn("bogus 0", out)
        self.assertIn("bogus", err)

    def test_every_category_dead_is_a_failure(self):
        code, _, err = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "bogus=9999", "--date", "2026-07-27"],
            lambda url: "<html><body></body></html>")
        self.assertEqual(code, 1)
        self.assertTrue(err.strip())

    def test_fetch_failure_exits_nonzero_with_a_message(self):
        def boom(url):
            raise IOError("connection refused")
        code, _, err = run_main(
            ["--site", "example-gym", "--club", "00000",
             "--category", "pool=1204", "--date", "2026-07-27"],
            boom)
        self.assertEqual(code, 1)
        self.assertIn("connection refused", err)

    def test_bad_category_argument_is_a_usage_error(self):
        with self.assertRaises(SystemExit) as caught:
            run_main(
                ["--site", "example-gym", "--club", "00000",
                 "--category", "nope", "--date", "2026-07-27"],
                _StubFetcher())
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
