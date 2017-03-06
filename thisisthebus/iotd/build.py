import os

from thisisthebus.settings.constants import DATA_DIR
import json


def process_iotds():
    iotd_dir = os.walk("%s/compiled/iotd" % DATA_DIR)
    iotd_files = list(iotd_dir)[0][2]

    iotds = {}
    for iotd_file in iotd_files:
        day = iotd_file.strip(".json")
        with open("%s/compiled/iotd/%s" % (DATA_DIR, iotd_file), 'r') as f:
            try:
                iotds[day] = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print("Had a problem with %s: %s" % (iotd_file, e))

    return iotds