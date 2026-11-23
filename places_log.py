"""One place per line of places_log.txt: `Name[ | lat, lng][ | YYYY-MM or unknown]`."""

import datetime
import os
import tempfile
from dataclasses import dataclass

LOG_FILENAME = "places_log.txt"
JSON_FILENAME = "places.geojson"
UNKNOWN_VISIT = "unknown"  # first visit too long ago to date


@dataclass
class Place:
    name: str
    coords: tuple[float, float] | None = None  # (lat, lng); skips geocoding
    visited: str | None = None  # first visit, "YYYY-MM" or UNKNOWN_VISIT


def parse_line(line):
    fields = [field.strip() for field in line.split("|")]
    if not fields[0]:
        return None
    place = Place(fields[0])
    for field in fields[1:]:
        if "," not in field:
            if field != UNKNOWN_VISIT:
                try:
                    datetime.datetime.strptime(field, "%Y-%m")
                except ValueError:
                    raise ValueError(f"visit {field!r} is not YYYY-MM or '{UNKNOWN_VISIT}'") from None
            place.visited = field
        else:
            lat, lng = field.split(",")
            place.coords = (float(lat), float(lng))
    return place


def format_line(place):
    fields = [place.name]
    if place.coords:
        fields.append(f"{place.coords[0]}, {place.coords[1]}")
    if place.visited:
        fields.append(place.visited)
    return " | ".join(fields)


def read(path):
    with open(f"{path}{LOG_FILENAME}", "r", encoding="UTF-8") as log_file:
        places = []
        for number, line in enumerate(log_file, 1):
            try:
                place = parse_line(line)
            except ValueError as err:
                raise ValueError(f"{LOG_FILENAME}:{number}: {line.strip()!r}: {err}") from err
            if place:
                places.append(place)
    names = [place.name for place in places]
    if len(set(names)) != len(names):
        raise ValueError(f"You have double entry in '{LOG_FILENAME}'; fix that.")
    return places


def write(path, places):
    """Replace the log in one step, so a failed write never truncates it."""
    text = "".join(format_line(place) + "\n" for place in places)
    with tempfile.NamedTemporaryFile("w", encoding="UTF-8", dir=path or ".", delete=False) as tmp_file:
        tmp_file.write(text)
    os.replace(tmp_file.name, f"{path}{LOG_FILENAME}")
