from __future__ import print_function

import json
import os

from thisisthebus.settings.constants import DATA_DIR
from thisisthebus.utils.questions import today_or_another_day
from thisisthebus.where.build import process_places


def new_location():
    process_places()
    print("-------------------------------------------")

    places_dir_listing = os.walk("%s/authored/places" % DATA_DIR)
    places = list(places_dir_listing)[0][2]

    place = None
    while not place:
        print("Which place?")
        for counter, place in enumerate(places):
            print("(%s) " % counter, place)
        try:
            place_int = int(input(""))
            place = places[place_int]
        except (ValueError, IndexError):
            continue

    print("Place meta: %s" % place)

    day = None
    while not day:
        day = today_or_another_day()

    location_meta = {"day": day, "place": place.replace(".yaml", "")}

    with open("%s/compiled/locations/%s" % (DATA_DIR, day), 'w') as f:
        f.write(json.dumps(location_meta))
