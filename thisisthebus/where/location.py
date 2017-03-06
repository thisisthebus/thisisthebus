from __future__ import print_function

import json
import os
import sys

from thisisthebus.settings.constants import DATA_DIR
from thisisthebus.where.build import process_places

sys.path.append('..')

from utils.questions import today_or_another_day

if __name__ == "__main__":

    process_places()

    places_dir_listing = os.walk("%s/authored/places" % DATA_DIR)
    places = list(places_dir_listing)[0][2]

    print("Which place?")
    for counter, place in enumerate(places):
        print("(%s) " % counter, place)

    place_int = int(input(""))
    place = places[place_int]

    print("Place meta: %s" % place)

    day = None
    while not day:
        day = today_or_another_day()

    location_meta = {"day": day, "place": place.replace(".yaml", "")}

    with open("%s/compiled/locations/%s" % (DATA_DIR, day), 'w') as f:
        f.write(json.dumps(location_meta))

