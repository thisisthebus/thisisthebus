from thisisthebus.settings.constants import DATA_DIR
image_data_dir = "%s/compiled/images" % DATA_DIR
import json
import os, sys
import hashlib

sys.path.append("/home/hubcraft/git/thisisthesitebuilder")

from thisisthesitebuilder.images.models import Image
Image.image_url_path = "apps/image/img/"
Image.image_file_path = "/home/hubcraft/git/thisisthebus/frontend/apps/image/img"


def fix_metadata():
    print("Processing Images.")

    for image_file in os.listdir(image_data_dir):
        day = image_file.strip(".json")
        with open("%s/compiled/images/%s" % (DATA_DIR, image_file), 'r') as f:
            images_metadata_for_this_day = json.loads(f.read())
            for image_metadata in images_metadata_for_this_day:

                # if image_metadata['slug'] == image_metadata['hash']:
                #     # Here's our first problem - we're confused about which is the slug and which is the hash.
                #     image_metadata

                try:
                    breakdown = image_metadata['full_url'].replace("______", "__").replace("____", "__").split("__")
                    if len(breakdown) == 3:
                        slug = breakdown[1]
                        hash = breakdown[2].split('.')[0]
                    elif len(breakdown) == 2:
                        if len(breakdown[1]) > len("e28f2286"):
                            slug = breakdown[1].split('.')[0]
                            hash = ""
                        else:
                            hash = breakdown[1].split('.')[0]
                            slug = ""
                        # hash = breakdown[1].split('.')[0]
                        # if not hash:
                        #     slug = breakdown[2]
                    else:
                       print("breakdown was %s: %s" % (len(breakdown), breakdown))
                except IndexError:
                    raise

                if not hash:
                    hash = image_metadata.get("hash")

                if not hash:
                    # Get the hash manually.
                    unchanged_path = Image.image_file_path + "/unchanged/" + \
                                     image_metadata['unchanged_url'].split("/")[-1]
                    if os.path.exists(unchanged_path):
                        with open(unchanged_path, "rb") as f:
                            image_bytes = f.read(1024)
                            hash = hashlib.md5(image_bytes).hexdigest()[:8]
                    else:
                        raise RuntimeError("Can't find the original.")

                if len(hash) > len("e28f2286"):
                    raise RuntimeError("Got a slug where we need a hash.")

                if slug == hash:
                    # Now that we have the hash, we may find that earlier, we mistook it for the slug.
                    slug = ""

                image_metadata['slug'] = slug
                image_metadata['hash'] = hash
                image_metadata['ext'] = image_metadata['full_url'].split('.')[-1]
                image_metadata['orig'] = image_metadata['unchanged_url'].split("/")[-1].split("__")[0]


        with open("%s/compiled/images/%s" % (DATA_DIR, image_file), 'w') as f:
            f.seek(0)
            f.write(json.dumps(images_metadata_for_this_day, sort_keys=True, indent=4,))
            f.truncate()

    return

def image_filename_fix(image, image_metadata):
    # Our thumb file doens't exist.
    # We'll put together paths based on the old URLs that we have.

    fullsize_path = Image.image_file_path + "/" + \
                    image_metadata['full_url'].split("/")[-1]
    thumb_path = Image.image_file_path + "/thumbs/" + \
                 image_metadata['thumb_url'].split("/")[-1]
    unchanged_path = Image.image_file_path + "/unchanged/" + \
                     image_metadata['unchanged_url'].split("/")[-1]
    ext = fullsize_path.split('.')[-1]
    # OK, now that we've put together a thumb file path from the URL, do we have that file?
    found_it_anyway = os.path.exists(thumb_path)
    if not found_it_anyway:
        thumb_path = thumb_path.replace("____", "__")
        found_it_anyway = os.path.exists(thumb_path)
    if not found_it_anyway:
        thumb_path = thumb_path.replace("____", "__")
        found_it_anyway = os.path.exists(thumb_path)

    if found_it_anyway:
        image_checksum = image_metadata.get("hash")
        if not image_checksum:
            with open(unchanged_path, "rb") as f:
                image_bytes = f.read(1024)
                image_checksum = hashlib.md5(image_bytes).hexdigest()[:8]
                image.hash = image_checksum

        if not image_checksum in unchanged_path:

            # OK, use the checksum to make a "new" file path.
            new_unchanged = unchanged_path.replace("____", "__").replace("." + ext,
                                                                         "__" + image_checksum + "." + ext)
            new_fullsize = fullsize_path.replace("____", "__").replace("." + ext,
                                                                       "__" + image_checksum + "." + ext)
            new_thumb = thumb_path.replace("____", "__").replace("." + ext,
                                                                 "__" + image_checksum + "." + ext)

            # Does the new file path match what we expect from our method?
            thumb_match = new_thumb == image.full_file_path("thumbs")
            full_match = new_fullsize == image.full_file_path("")
            unchanged_match = new_unchanged == image.full_file_path("unchanged")

            if thumb_match and full_match and unchanged_match:
                print("Renaming %s" % thumb_path)
                os.rename(thumb_path, new_thumb)
                try:
                    os.rename(fullsize_path, new_fullsize)
                except FileNotFoundError:
                    os.rename(fullsize_path.replace("____", "__"), new_fullsize)
                try:
                    os.rename(unchanged_path, new_unchanged)
                except FileNotFoundError:
                    os.rename(unchanged_path.replace("____", "__"), new_unchanged)
            else:
                image.full_file_path("unchanged")
                raise RuntimeError("Filenames still didn't match.")

        dunder_fixed = False
        if "____" in thumb_path and not os.path.exists(image.full_file_path("thumbs")):
            os.rename(thumb_path, thumb_path.replace("____", "__"))
            dunder_fixed = True
        if "____" in unchanged_path and not os.path.exists(image.full_file_path("unchanged")):
            os.rename(unchanged_path, unchanged_path.replace("____", "__"))
            dunder_fixed = True
        if "____" in fullsize_path and not os.path.exists(image.full_file_path("")):
            os.rename(fullsize_path, fullsize_path.replace("____", "__"))
            dunder_fixed = True
        if dunder_fixed:
            print("Fixed dunder for %s" % image_checksum)
            return

        return # What happened here?

    else:
        print("Absolutely unable to find %s" % thumb_path)

def audit_images(fix_things=False):
    found = 0
    hashes = []

    fullsize_count = len(next(os.walk(Image.image_file_path))[2])
    unchanged_count = len(next(os.walk(Image.image_file_path + "/unchanged"))[2])
    thumb_count = len(next(os.walk(Image.image_file_path + "/thumbs"))[2])


    for image_file in os.listdir(image_data_dir):
        day = image_file.strip(".json")

        with open("%s/compiled/images/%s" % (DATA_DIR, image_file), 'r') as f:
            images_metadata_for_this_day = json.loads(f.read())
            for image_metadata in images_metadata_for_this_day:
                image = Image(date=day, **image_metadata)
                if image.hash in hashes:
                    print("Repeat hash found: {}".format(image.hash))
                else:
                    hashes.append(image.hash)


                thumb_exists = image.check_thumb()
                full_exists = image.check_full()
                unchanged_exists = image.check_unchanged()

                if fix_things and not thumb_exists:
                    image_filename_fix(image, image_metadata)

                if thumb_exists and full_exists and unchanged_exists:
                    found += 1

    print("Found {} images, {} hashes".format(found, len(hashes)))
    print("Counts: thumbs {}, full {}, unchanged {}".format(thumb_count, fullsize_count, unchanged_count))

if __name__ == "__main__":
    # fix_metadata()
    audit_images(True)