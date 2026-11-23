import os
import tempfile
import unittest

from places_log import LOG_FILENAME, UNKNOWN_VISIT, Place, format_line, parse_line, read, write


class ParseLineTest(unittest.TestCase):
    def test_name_only(self):
        self.assertEqual(parse_line("Cairo, Egypt\n"), Place("Cairo, Egypt"))

    def test_blank_line_is_no_place(self):
        self.assertIsNone(parse_line("   \n"))

    def test_coords(self):
        self.assertEqual(
            parse_line("Drake Passage, Southern Ocean | -57.45, -65.6167"),
            Place("Drake Passage, Southern Ocean", coords=(-57.45, -65.6167)),
        )

    def test_visit_month(self):
        self.assertEqual(
            parse_line("Cairo, Egypt | 2019-03"),
            Place("Cairo, Egypt", visited="2019-03"),
        )

    def test_coords_and_visit_month(self):
        self.assertEqual(
            parse_line("Arenas Del Mar, Costa Rica | 9.39774, -84.16258 | 2026-11"),
            Place("Arenas Del Mar, Costa Rica", coords=(9.39774, -84.16258), visited="2026-11"),
        )

    def test_unknown_visit(self):
        self.assertEqual(parse_line("Pisa, Italy | unknown"), Place("Pisa, Italy", visited=UNKNOWN_VISIT))

    def test_impossible_month_raises(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM or 'unknown'"):
            parse_line("Cairo, Egypt | 2019-13")

    def test_malformed_field_raises(self):
        with self.assertRaises(ValueError):
            parse_line("Cairo, Egypt | March 2019")


class FormatLineTest(unittest.TestCase):
    def test_round_trip(self):
        for line in [
            "Cairo, Egypt",
            "Cairo, Egypt | 2019-03",
            "Pisa, Italy | unknown",
            "Drake Passage, Southern Ocean | -57.45, -65.6167",
            "Arenas Del Mar, Costa Rica | 9.39774, -84.16258 | 2026-11",
        ]:
            self.assertEqual(format_line(parse_line(line)), line)


class ReadTest(unittest.TestCase):
    def test_duplicate_name_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, LOG_FILENAME), "w", encoding="UTF-8") as log_file:
                log_file.write("Cairo, Egypt\n\nCairo, Egypt | 2019-03\n")
            with self.assertRaises(ValueError):
                read(tmp + "/")

    def test_bad_line_error_names_the_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, LOG_FILENAME), "w", encoding="UTF-8") as log_file:
                log_file.write("Cairo, Egypt\nNara, Japan | 2019-3x\n")
            with self.assertRaisesRegex(ValueError, "places_log.txt:2: .*Nara, Japan"):
                read(tmp + "/")


class WriteTest(unittest.TestCase):
    def test_failed_write_keeps_the_old_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, LOG_FILENAME)
            with open(path, "w", encoding="UTF-8") as log_file:
                log_file.write("Cairo, Egypt\n")
            with self.assertRaises(IndexError):
                write(tmp + "/", [Place("Nara, Japan"), Place("Bad", coords=(1.0,))])
            with open(path, encoding="UTF-8") as log_file:
                self.assertEqual(log_file.read(), "Cairo, Egypt\n")
            self.assertEqual(os.listdir(tmp), [LOG_FILENAME])


if __name__ == "__main__":
    unittest.main()
