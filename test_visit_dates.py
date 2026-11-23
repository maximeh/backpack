import contextlib
import io
import unittest

from visit_dates import earliest_photo_month, first_added_months, first_visit

GIT_LOG = """\x002012-09
diff --git a/places_log.txt b/places_log.txt
--- /dev/null
+++ b/places_log.txt
@@ -0,0 +1,2 @@
+Paris, France
+Cairo, Egypt
\x002013-01
diff --git a/places_log.txt b/places_log.txt
--- a/places_log.txt
+++ b/places_log.txt
@@ -2,0 +3 @@
-Cairo, Egypt
+Cairo, Egypt | 30.04, 31.23
+Maldives
"""

PARIS = (48.8566, 2.3522)
VERSAILLES = (48.8049, 2.1204)  # 18 km from Paris
LONDON = (51.5074, -0.1278)


class FirstAddedMonthsTest(unittest.TestCase):
    def test_skips_history_lines_in_an_old_format(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            months = first_added_months("\x002012-09\n+Foo | approx\n+Nara, Japan\n")
        self.assertEqual(months, {"Nara, Japan": "2012-09"})
        self.assertIn("Skipping old log line 'Foo | approx'", stderr.getvalue())

    def test_month_of_first_commit_adding_each_name(self):
        self.assertEqual(
            first_added_months(GIT_LOG),
            {"Paris, France": "2012-09", "Cairo, Egypt": "2012-09", "Maldives": "2013-01"},
        )


class EarliestPhotoMonthTest(unittest.TestCase):
    def test_earliest_photo_within_radius(self):
        photos = [("2019-05", *VERSAILLES), ("2016-02", *LONDON), ("2017-08", *PARIS)]
        self.assertEqual(earliest_photo_month(PARIS, photos), "2017-08")

    def test_radius_bounds_match(self):
        self.assertEqual(earliest_photo_month(PARIS, [("2015-01", *VERSAILLES)], radius_km=20), "2015-01")
        self.assertIsNone(earliest_photo_month(PARIS, [("2015-01", *VERSAILLES)], radius_km=15))

    def test_no_photo_nearby(self):
        self.assertIsNone(earliest_photo_month(PARIS, [("2016-02", *LONDON)]))


class FirstVisitTest(unittest.TestCase):
    def test_earliest_known_month_wins(self):
        self.assertEqual(first_visit("2018-04", "2012-09"), "2012-09")
        self.assertEqual(first_visit("2011-04", "2012-09"), "2011-04")

    def test_one_source_missing(self):
        self.assertEqual(first_visit(None, "2012-09"), "2012-09")
        self.assertEqual(first_visit("2011-04", None), "2011-04")
        self.assertIsNone(first_visit(None, None))


if __name__ == "__main__":
    unittest.main()
