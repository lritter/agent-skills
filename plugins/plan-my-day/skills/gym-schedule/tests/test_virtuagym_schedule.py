import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from virtuagym_schedule import parse_time_range


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


if __name__ == "__main__":
    unittest.main()
