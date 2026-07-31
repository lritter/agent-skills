import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from virtuagym_schedule import Session, parse_time_range, parse_week


class TestParseTimeRange(unittest.TestCase):
    def test_morning_range(self):
        self.assertEqual(parse_time_range("06:30 am - 07:25 am"), ("06:30", "07:25"))

    def test_noon_stays_twelve(self):
        self.assertEqual(parse_time_range("12:00 pm - 12:45 pm"), ("12:00", "12:45"))

    def test_leading_zero_pm_hour(self):
        # Real fixture row. 01:45 pm must become 13:45, not 01:45.
        self.assertEqual(parse_time_range("12:00 pm - 01:45 pm"), ("12:00", "13:45"))

    def test_midnight_becomes_zero(self):
        # Synthetic: the fixtures contain no 12:xx am rows.
        self.assertEqual(parse_time_range("12:30 am - 01:00 am"), ("00:30", "01:00"))

    def test_surrounding_whitespace_tolerated(self):
        self.assertEqual(parse_time_range("\n  06:30 am - 07:25 am  "), ("06:30", "07:25"))

    def test_unparseable_raises(self):
        with self.assertRaises(ValueError):
            parse_time_range("all day")


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
        # 266 pool grid cells collapse to 87 real rows; the rest are layout padding.
        self.assertEqual(len(self.pool.sessions), 87)
        self.assertEqual(len(self.group.sessions), 67)
        for session in self.pool.sessions:
            self.assertTrue(session.name)
            self.assertTrue(session.start)

    def test_date_is_day_month_year_not_month_day(self):
        # 01-08-2026 is 1 August, not 8 January. Getting this backwards is silent.
        self.assertIn("2026-08-01", self.pool.dates)
        self.assertNotIn("2026-01-08", self.pool.dates)

    def test_weekday_name(self):
        first = [s for s in self.pool.sessions if s.date == "2026-07-27"][0]
        self.assertEqual(first.weekday, "Monday")

    def test_concurrent_sessions_are_not_deduped(self):
        # Two different pool programs genuinely share 06:30-07:25.
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
        # The fixture literally contains "AOA Strength and  Conditioning".
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


if __name__ == "__main__":
    unittest.main()
