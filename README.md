# backpack 🎒🌍

See my [travel map](http://maximeh.github.io/backpack)

This repo contains a very small website to list all the places I have ever visited in the world.
Rule is simple: I have to have spent at least a night in the location.

# Requirements
You will need a Google Maps [API key](https://developers.google.com/maps/documentation/geocoding/get-api-key).
It must be placed in a 'gmaps.key' file at the root of this repo.

# How does it work?
It will "translate" human readable addresses placed in `places_log.txt` into a [Geojson](https://en.wikipedia.org/wiki/GeoJSON) file that can be displayed by [Leaflet](https://leafletjs.com).

The addresses only need to be understood by Google Maps Geocode API; so you can be as loose or precise as you want.
Examples
   - New York City, USA
   - 1 This St, Porters Lake, NS B3E 1H4, Canada
   
# How do I add new places?
## Manually
Edit `places_log.txt` and add the address.
The only limitation is one address per line.

## Using a git pre-commit hook

Create a `post-receive` script in your `.git/hooks` directory with the following content:
*Note* : Don't forget to `chmod +x post-receive`, or it will not work.

    #!/bin/sh
    if [ "$(git name-rev --name-only HEAD)" != "main" ]; then
        python geocode.py
    fi

For each commit, it'll run that script which will take the content of `places_log.txt` and update `places.geojson` if need be.

Fork the project and start your own! Do share your travel map if you do!
Feel free to contribute features/ideas.

