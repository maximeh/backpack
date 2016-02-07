#! /usr/bin/python -B
# -*- coding: utf-8 -*-

import json
import sys
if (sys.version_info > (3, 0)):
    from urllib.request import urlopen
    from urllib.parse import urlencode
else:
    from urllib import urlopen, urlencode

URL = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
JSON_FILENAME = "places.geojson"
KEY_FILENAME = "gmaps.key"

def find_lat_lng(key, place):
    point = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [None, None]},
        "properties": {"name": place, 'show_on_map': False}
    }
    req = urlopen(URL % (urlencode({'q':place}), key))
    data = req.read().decode("utf-8")
    if data == []:
        return None
    geo_value = json.loads(data)
    if geo_value['status'] != "OK":
        print("Could not find address for '%s'" % place)
        return None
    point["geometry"]["coordinates"] = [
        float(geo_value['results'][0]['geometry']['location']['lng']),
        float(geo_value['results'][0]['geometry']['location']['lat'])]
    point["properties"]["show_on_map"] = True
    return point

def main(path=""):

    with open("%s%s" % (path, KEY_FILENAME), 'r') as key_file:
        key = key_file.readline().strip()

    json_path = "%s%s" % (path, JSON_FILENAME)
    try:
        with open("%splaces_log.txt" % path, 'r') as places_file:
            places = places_file.readlines()
            places = [pl.strip() for pl in places]
    except IOError as err:
        print("I/O error({0}): {1}".format(err.errno, err.strerror))
        return 1

    places_gps = {
        "type": "FeatureCollection",
        "features": [],
    }

    try:
        with open(json_path, 'r') as places_gps_file:
            places_gps = json.load(places_gps_file)
    except:
        # Either the file was not here on the JSON was invalid.
        # We will rewrite the whole file then.
        pass

    for pl in places_gps['features']:
        if pl['properties']['name'] in places:
            # We already know that place
            places.remove(pl['properties']['name'])
        else:
            # This place should not be here anymore
            places_gps['features'].remove(pl)

    # Find the gps coordinates of the new places
    for pl in places:
        point = find_lat_lng(key, pl)
        if point is None:
            continue
        places_gps['features'].append(point)

    # Rewrite totally the file, it's slow but let us handle deleted entry
    # in places_log.txt easily
    with open(json_path, 'w') as places_file:
        places_file.write(json.dumps(places_gps, sort_keys=True, indent=4))
    return 0

if __name__ == '__main__':
    sys.exit(main())
