#! /usr/bin/python3 -B
# -*- coding: utf-8 -*-
"""Fill the first-visit month of each place in places_log.txt that has none.

The month is the earliest of: the first geotagged photo near the place, and the
first commit that logged it. Both come after the real visit, so the earliest wins.
"""

import collections
import datetime
import json
import math
import os
import sqlite3
import subprocess
import sys

import places_log

PHOTOS_DB = "~/Pictures/Photos Library.photoslibrary/database/Photos.sqlite"
LOGS_IN_HISTORY = ["locations.txt", places_log.LOG_FILENAME]  # the log was renamed in 2012
COMMIT_MARKER = "\0"  # git prints it for %x00
# SHORTCUT: one radius for cities and single addresses; ceiling: photos taken
# around a home city date every address there; upgrade: when such dates are wrong.
NEARBY_KM = 25


def first_added_months(git_log):
    """Map each logged name to the month of the first commit adding it."""
    months = {}
    for line in git_log.splitlines():
        if line.startswith(COMMIT_MARKER):
            month = line[len(COMMIT_MARKER):]
        elif line.startswith("+") and not line.startswith("+++"):
            try:
                place = places_log.parse_line(line[1:])
            except ValueError as err:
                print(f"Skipping old log line {line[1:]!r}: {err}", file=sys.stderr)
                continue
            if place:
                months.setdefault(place.name, month)
    return months


def distance_km(a, b):
    lat1, lng1, lat2, lng2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def earliest_photo_month(coords, photos, radius_km=NEARBY_KM):
    """photos holds (month, lat, lng) tuples."""
    return min(
        (month for month, lat, lng in photos if distance_km(coords, (lat, lng)) <= radius_km),
        default=None,
    )


def first_visit(photo_month, logged_month):
    return min(filter(None, (photo_month, logged_month)), default=None)


def read_photos(db_path):
    epoch = datetime.datetime(2001, 1, 1)
    db = sqlite3.connect(f"file:{os.path.expanduser(db_path)}?mode=ro", uri=True)
    rows = db.execute(
        "SELECT ZDATECREATED, ZLATITUDE, ZLONGITUDE FROM ZASSET"
        " WHERE ZTRASHEDSTATE = 0 AND ZDATECREATED IS NOT NULL"
        " AND ZLATITUDE BETWEEN -90 AND 90 AND ZLATITUDE != 0"
    ).fetchall()
    db.close()
    return [((epoch + datetime.timedelta(seconds=date)).strftime("%Y-%m"), lat, lng) for date, lat, lng in rows]


def read_git_log(path):
    return subprocess.run(
        ["git", "log", "--reverse", "--format=%x00%ad", "--date=format:%Y-%m",
         "-p", "-U0", "--", *LOGS_IN_HISTORY],
        cwd=path or ".", capture_output=True, text=True, check=True,
    ).stdout


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ""

    log = places_log.read(path)
    with open(f"{path}{places_log.JSON_FILENAME}", "r", encoding="UTF-8") as json_file:
        geocoded = {
            feat["properties"]["name"]: tuple(reversed(feat["geometry"]["coordinates"]))
            for feat in json.load(json_file)["features"]
        }
    photos = read_photos(PHOTOS_DB)
    logged = first_added_months(read_git_log(path))

    sources = collections.Counter()
    for place in log:
        if place.visited:
            continue
        coords = place.coords or geocoded.get(place.name)
        photo_month = earliest_photo_month(coords, photos) if coords else None
        place.visited = first_visit(photo_month, logged.get(place.name))
        sources["none" if not place.visited else "photo" if place.visited == photo_month else "git"] += 1

    places_log.write(path, log)
    print(f"Dated {sources['photo']} places from photos, {sources['git']} from git; {sources['none']} left undated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
