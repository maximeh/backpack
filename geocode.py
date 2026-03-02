#! /usr/bin/python -B
# -*- coding: utf-8 -*-

import json
import sys

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

URL = "https://maps.googleapis.com/maps/api/geocode/json"
JSON_FILENAME = "places.geojson"
KEY_FILENAME = "gmaps.key"


def find_lat_lng(session, key, place):

    point = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [None, None]},
        "properties": {"name": place, "show_on_map": True},
    }

    req = session.get(URL, params={"address": place, "key": key})
    geo_value = req.json()
    if geo_value["status"] != "OK":
        print(f"Could not find address for '{place}'")
        point["properties"]["show_on_map"] = False
        return None

    lat_lng = geo_value["results"][0]["geometry"]["location"]
    point["geometry"]["coordinates"] = [lat_lng["lng"], lat_lng["lat"]]

    return point


def main():

    try:
        path = sys.argv[1]
    except IndexError:
        path = ""

    with open(f"{path}{KEY_FILENAME}", "r", encoding="UTF-8") as key_file:
        key = key_file.readline().strip()

    json_path = f"{path}{JSON_FILENAME}"
    try:
        with open(f"{path}places_log.txt", "r", encoding="UTF-8") as places_file:
            places = []
            manual_coords = {}
            for line in places_file:
                line = line.strip()
                if not line:
                    continue
                if "|" in line:
                    name, coords_str = line.split("|", 1)
                    name = name.strip()
                    lat_str, lng_str = coords_str.strip().split(",")
                    manual_coords[name] = (float(lat_str.strip()), float(lng_str.strip()))
                    places.append(name)
                else:
                    places.append(line)
            if len(set(places)) != len(places):
                print("You have double entry in 'places_log.txt'; fix that.")
                return 1
    except IOError as err:
        print(f"I/O error({err.errno}): {err.strerror}")
        return 1

    try:
        with open(json_path, "r", encoding="UTF-8") as places_gps_file:
            data = json.load(places_gps_file)
            features = data["features"]
    except:
        # Either the file was not here on the JSON was invalid.
        # We will rewrite the whole file then.
        features = []

    kept_features = []
    for feat in features:
        name = feat["properties"]["name"]
        if name in places:
            if name not in manual_coords:
                kept_features.append(feat)
                places.remove(name)
            # Manual coords entries stay in places to be re-added below
        # Features not in places are dropped (removed from log)
    features = kept_features

    # Create a session object with some backoff and retry to avoid hitting
    # quota limits
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Find the gps coordinates of the new places
    for place in places:
        if place in manual_coords:
            lat, lng = manual_coords[place]
            point = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {"name": place, "show_on_map": True},
            }
        else:
            point = find_lat_lng(session, key, place)
            if point is None:
                continue
        features.append(point)

    features = sorted(features, key=lambda x: x["properties"]["name"])

    places_gps = {
        "type": "FeatureCollection",
        "features": features,
    }

    # Rewrite totally the file, it's slow but let us handle deleted entry
    # in places_log.txt easily
    with open(json_path, "w", encoding="UTF-8") as places_file:
        data = json.dumps(places_gps, sort_keys=True, indent=4, separators=(",", ":"))
        places_file.write(data)


if __name__ == "__main__":
    sys.exit(main())
