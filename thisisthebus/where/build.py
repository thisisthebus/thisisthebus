import json
import os

from thisisthebus.settings.constants import DATA_DIR
from thisisthebus.where.models import Place

PLACES_DIR = "%s/authored/places" % DATA_DIR

def process_locations():
    locations_dir_listing = os.walk("%s/compiled/locations" % DATA_DIR)
    location_files = list(locations_dir_listing)[0][2]
    location_files.remove(
        "latest")  # Remove the string "latest" from the list of locations in order to properly determine the most recent date

    locations = {}
    for day in location_files:
        with open("%s/compiled/locations/%s" % (DATA_DIR, day), 'r') as f:
            try:
                locations[day] = json.loads(f.read())
            except Exception as e:
                pass


    return locations


def process_places(wait_at_end=False):
    print("Processing Places from %s" % PLACES_DIR)
    authored_places_dir = os.walk(PLACES_DIR)

    places = {}
    new_places = 0

    for yaml_file in list(authored_places_dir)[0][2]:
        place = Place.from_authored_yaml(yaml_file)
        place_meta, created = place.compile()
        if created:
            new_places += 1
        place_name = yaml_file.replace('.yaml', '')
        places[place_name] = place_meta

    print("Processed %s Places" % new_places)

    if wait_at_end:
        input()

    return places

