backpack
=======

See the [example](http://maximeh.github.com/backpack)

A very small website to track down all the places I have ever visited in the
world.
Just fork the project and add features if you want to !

Actually, you just edit places_log.txt and the address of the new location.
The only limitation is one address per line.

You will need a Google Maps [API key](https://developers.google.com/maps/documentation/geocoding/get-api-key).
It must be placed in a 'gmaps.key' file at the root of this repo.

Using a git pre-commit hook
---------------------------
Create a post-receive script in your .git/hooks directory like so :

    #!/bin/sh
    if [ "$(git name-rev --name-only HEAD)" != "master" ]; then
        python geocode.py
    fi

Each time you will commits, if something is new in places_log.txt, it will
be added into places.geojson

Note : Don't forget to chmod +x post-receive, or it will not work.

Enjoy ! :)

