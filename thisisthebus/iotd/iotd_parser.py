from PIL import Image, ExifTags
import datetime
import sys
import json

from site_builders import complete_build
from thisisthebus.settings.constants import DATA_DIR, FRONTEND_DIR

MAX_SIZE = 1600.0
THUMB_SIZE = 400


def autorotate(image_file, orientation):
    if orientation == 3:
        image_file = image_file.rotate(180, expand=True)
    elif orientation == 6:
        image_file = image_file.rotate(270, expand=True)
    elif orientation == 8:
        image_file = image_file.rotate(90, expand=True)
    return image_file


def get_filename_for_day(day):
    return "%s/compiled/iotd/%s.json" % (DATA_DIR, day)


def which_day(exif_date):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print("Which day is this IOTD for?")
    if exif_date:
        print("1) The day it was taken (%s)" % exif_date)
    else:
        print("(This image is from an unknown date.)")
    print("2) Today (%s)" % today)
    print("3) Some other date")

    response = input("Enter 1-3: ")

    try:
        response = int(response)
    except ValueError:
        return

    if response == 1:
        if not exif_date:
            print("I told you - we don't know when the image was taken.  Try again.")
            day = None
        else:
            day = exif_date
    elif response == 2:
        day = today
    elif response == 3:
        day = str(input("Enter YYYY-MM-DD\n"))
    else:
        return
    return day


def ask_for_caption():
    return str(input("Enter a caption - say, 140 chars or so: "))


def write_to_file(filename, payload):
    with open(filename, "w") as f:
        f.write(payload)
        print("writing %s:" % filename)
        print(payload)
        print("-----------------------------------")


def parse_iotd(image_filename):

    image_filename = image_filename
    img = Image.open(image_filename)
    try:
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
        orientation = exif.get('Orientation')

        abridged_exif = {k: exif[k] for k in (
            'ApertureValue', 'DateTime', 'Flash', 'FocalLength', 'GPSInfo', 'Model', 'Orientation', 'ShutterSpeedValue')}

        day_image_was_taken = abridged_exif['DateTime'].split()[0].replace(':', "-")

    except AttributeError:
        # We apparently don't have exif data.
        orientation = None
        day_image_was_taken = None

    print("\n====================================")
    print("OK, let's add %s to our IOTD." % sys.argv[1])

    # Figure out what day this is an IOTD for.

    day = None

    while not day:
        day = which_day(day_image_was_taken)

    # Keep asking for a caption until we get a caption.
    new_iotd = {'caption': None}
    while not new_iotd['caption']:
        new_iotd['caption'] = ask_for_caption()

    full_filename = '/apps/iotd/img/%s!%s.jpg' % (day, new_iotd['caption'].replace(' ', '-'))
    thumb_filename = '/apps/iotd/img/%s!%s!thumb.jpg' % (day, new_iotd['caption'].replace(' ', '-'))

    new_iotd['full_url'] = full_filename
    new_iotd['thumb_url'] = thumb_filename

    h = float(img.size[0])
    w = float(img.size[1])
    full_resize_ratio = min(MAX_SIZE / w, MAX_SIZE / h)
    thumb_resize_ratio = min(THUMB_SIZE / w, THUMB_SIZE / h)

    full_size = w * full_resize_ratio, h * full_resize_ratio
    thumb_size = w * thumb_resize_ratio, h * thumb_resize_ratio

    try:
        with open(get_filename_for_day(day), 'r') as f:
            this_day_meta = json.loads(f.read())
    except FileNotFoundError:
        this_day_meta = []

    this_day_meta.append(new_iotd)

    write_to_file(filename=get_filename_for_day(day), payload=json.dumps(this_day_meta, indent=2))

    print("full: resizing from (%s, %s) to %s" % (w, h, full_size))
    if orientation:
        img = autorotate(img, orientation)
    img.thumbnail(full_size, Image.ANTIALIAS)
    img.save(FRONTEND_DIR + full_filename, "JPEG")
    print("------------------------------------")
    print("thumb: resizing from (%s, %s) to %s" % (w, h, thumb_size))
    thumb = Image.open(image_filename)
    if orientation:
        thumb = autorotate(thumb, orientation)
    thumb.thumbnail(thumb_size, Image.ANTIALIAS)
    thumb.save((FRONTEND_DIR + thumb_filename), "JPEG")
    print("====================================\n")
    input("done!")


    # import django
    #
    # django.setup()
    # complete_build()

