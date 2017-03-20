import os

from thisisthebus.settings.constants import DATA_DIR
import json

image_data_dir = "%s/compiled/images" % DATA_DIR


def process_images():
    print("Processing Images.")

    iotds = {}
    for iotd_file in os.listdir(image_data_dir):
        day = iotd_file.strip(".json")
        with open("%s/compiled/images/%s" % (DATA_DIR, iotd_file), 'r') as f:
            iotds[day] = json.loads(f.read())

    return iotds