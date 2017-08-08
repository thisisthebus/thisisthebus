import datetime
from collections import OrderedDict

import maya
from PIL import Image, ExifTags
from django.template.loader import get_template

from build.ensure_build_path import add_project_dir_to_path
from thisisthebus.settings.constants import FRONTEND_DIR
from thisisthesitebuilder.images import process_images


def parse_exif_datetime(exif_datetime_string):
    return datetime.datetime.strptime(exif_datetime_string + 'UTC', '%Y:%m:%d %H:%M:%S%Z')

if __name__ == "__main__":
    add_project_dir_to_path()
    import django
    django.setup()

    images_dict = process_images()
    for day, image_list in images_dict.items():
        for image in image_list:

            unchanged_filename = "%s/%s" % (FRONTEND_DIR, image['unchanged_url'])
            img = Image.open(unchanged_filename)

            exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
            exif_datetime = parse_exif_datetime(exif['DateTime'])

            image_day = maya.when(day, timezone="US/Eastern")
            image_day.add()
            image_time = exif_datetime.time()
            image['time'] = exif_datetime
            image['iso8601'] = image_day.add(hours=image_time.hour, minutes=image_time.minute, seconds=image_time.second).iso8601()
            image['new_datetime'] = image_day.add(hours=image_time.hour, minutes=image_time.minute, seconds=image_time.second).datetime(to_timezone="US/Eastern", naive=True)

    t = get_template('image-table.html')
    sorted_images = OrderedDict(sorted(images_dict.items(), key=lambda i: i[0]))
    image_table_html = t.render({'images': sorted_images})

    with open("%s/apps/image/image-table.html" % FRONTEND_DIR, "w+") as f:
        f.write(image_table_html)
