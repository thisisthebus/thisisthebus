import datetime
import json
import shutil
import sys
import hashlib

from PIL import Image, ExifTags
from django.utils.text import slugify

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
    return "%s/compiled/images/%s.json" % (DATA_DIR, day)


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


def what_time(exif_date):
    print("What time?")
    if exif_date:
        print("1) The time it was taken (%s)" % exif_date)
    else:
        print("(This image is from an unknown date.)")
    print("2) Midnight")
    print("3) Some other time")

    response = input("Enter 1-3: ")

    try:
        response = int(response)
    except ValueError:
        return

    if response == 1:
        if not exif_date:
            print("I told you - we don't know when the image was taken.  Try again.")
            time = None
        else:
            time = exif_date
    elif response == 2:
        time = "00:00:00"
    elif response == 3:
        time = str(input("Enter hh:mm:ss\n"))
    else:
        return
    return time

def ask_for_caption():
    return str(input("Enter a caption - say, 140 chars or so: "))

def ask_for_tags():
    tag_str = str(input("Tags, separated by comma: "))
    return tag_str.split(',')


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

        abridged_exif = {}
        for k in ('ApertureValue', 'DateTime', 'Flash', 'FocalLength', 'GPSInfo', 'Model', 'Orientation', 'ShutterSpeedValue'):
            abridged_exif[k] = exif.get(k)

        day_image_was_taken = abridged_exif['DateTime'].split()[0].replace(':', "-")
        time_image_was_taken = abridged_exif['DateTime'].split()[1]

    except AttributeError:
        # We apparently don't have exif data.
        orientation = None
        day_image_was_taken = None
        time_image_was_taken = None

    print("\n====================================")
    print("OK, let's add %s to our IOTD." % sys.argv[1])

    # Figure out what day this is an IOTD for.

    day = None

    while not day:
        day = which_day(day_image_was_taken)

    time = None
    while not time:
        time = what_time(time_image_was_taken)

    # Start our new meta dict by asking for a caption.
    new_iotd = {'caption': ask_for_caption()}
    new_iotd['tags'] = ask_for_tags()

    with open(image_filename, "rb") as f:
        image_bytes = f.read(1024)
        image_checksum = hashlib.md5(image_bytes).hexdigest()[:8]

    file_detail = slugify(new_iotd['caption'][:30]) + "__" if new_iotd['caption'] else ""
    file_detail += image_checksum
    extension = image_filename.split('.')[-1]

    unchanged_filename = '/apps/iotd/img/unchanged/%s__%s.%s' % (img.filename.split('/')[-1], file_detail, extension)
    full_filename = '/apps/iotd/img/%s__%s.%s' % (day, file_detail, extension)
    thumb_filename = '/apps/iotd/img/thumbs/%s__%s.%s' % (day, file_detail, extension)

    new_iotd['unchanged_url'] = unchanged_filename
    new_iotd['full_url'] = full_filename
    new_iotd['thumb_url'] = thumb_filename
    new_iotd['time'] = time

    h = float(img.size[0])
    w = float(img.size[1])
    full_resize_ratio = min(MAX_SIZE / w, MAX_SIZE / h)
    thumb_resize_ratio = min(THUMB_SIZE / w, THUMB_SIZE / h)

    full_size = h * full_resize_ratio, w * full_resize_ratio
    thumb_size = h * thumb_resize_ratio, w * thumb_resize_ratio

    try:
        with open(get_filename_for_day(day), 'r') as f:
            this_day_meta = json.loads(f.read())
    except FileNotFoundError:
        this_day_meta = []

    this_day_meta.append(new_iotd)

    write_to_file(filename=get_filename_for_day(day), payload=json.dumps(this_day_meta, indent=2))

    print("Saving original (%s, %s)" % (w, h))
    shutil.copyfile(image_filename, FRONTEND_DIR + unchanged_filename)

    print("full: resizing from (%s, %s) to %s" % (w, h, full_size))
    if orientation:
        img = autorotate(img, orientation)
    img.thumbnail(full_size, Image.ANTIALIAS)
    img.save(FRONTEND_DIR + full_filename, "JPEG", quality=60, optimize=True, progressive=True)
    print("------------------------------------")
    print("thumb: resizing from (%s, %s) to %s" % (w, h, thumb_size))
    thumb = Image.open(image_filename)
    if orientation:
        thumb = autorotate(thumb, orientation)
    thumb.thumbnail(thumb_size, Image.ANTIALIAS)
    thumb.save((FRONTEND_DIR + thumb_filename), "JPEG")
    print("====================================\n")
    input("done!")

