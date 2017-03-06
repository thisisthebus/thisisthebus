import json
import os

from thisisthebus.settings.constants import DATA_DIR
from thisisthebus.where.models import Place


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


def process_places():
    authored_places_dir = os.walk("%s/authored/places" % DATA_DIR)

    places = {}

    for yaml_file in list(authored_places_dir)[0][2]:
        place = Place.from_authored_yaml(yaml_file)
        place_meta = place.compile()
        place_name = yaml_file.replace('.yaml', '')
        places[place_name] = place_meta

    return places

