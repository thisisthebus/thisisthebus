import maya
import datetime, pytz
from PIL import Image, ExifTags
from django.template.loader import get_template

from build.ensure_build_path import add_project_dir_to_path
from thisisthebus.iotd.build import process_iotds
from thisisthebus.settings.constants import FRONTEND_DIR

from collections import OrderedDict


def parse_exif_datetime(exif_datetime_string):
    return datetime.datetime.strptime(exif_datetime_string + 'UTC', '%Y:%m:%d %H:%M:%S%Z')

if __name__ == "__main__":
    add_project_dir_to_path()
    import django
    django.setup()

    iotds_dict = process_iotds()
    for day, iotd_list in iotds_dict.items():
        for iotd in iotd_list:

            unchanged_filename = "%s/%s" % (FRONTEND_DIR, iotd['unchanged_url'])
            img = Image.open(unchanged_filename)

            exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
            exif_datetime = parse_exif_datetime(exif['DateTime'])

            image_day = maya.when(day, timezone="US/Eastern")
            image_day.add()
            image_time = exif_datetime.time()
            iotd['time'] = exif_datetime
            iotd['iso8601'] = image_day.add(hours=image_time.hour, minutes=image_time.minute, seconds=image_time.second).iso8601()
            iotd['new_datetime'] = image_day.add(hours=image_time.hour, minutes=image_time.minute, seconds=image_time.second).datetime(to_timezone="US/Eastern", naive=True)

    t = get_template('iotd-table.html')
    sorted_iotds = OrderedDict(sorted(iotds_dict.items(), key=lambda i: i[0]))
    iotd_table_html = t.render({'images': sorted_iotds})

    with open("%s/apps/iotd/image-table.html" % FRONTEND_DIR, "w+") as f:
        f.write(iotd_table_html)
