from thisisthebus.daily_log.build import process_summaries
from thisisthebus.where.build import process_locations, process_places
from thisisthesitebuilder.images.build import process_images

SUMMARIES = process_summaries()
PLACES = process_places()
LOCATIONS = process_locations(PLACES)
IMAGES, IMAGES_BY_HASH, IMAGES_BY_SLUG, NON_UNIQUE_HASHES, NON_UNIQUE_SLUGS = process_images()


def lookup_image_by_hash(hash):
    if not hash in NON_UNIQUE_HASHES:
        return IMAGES_BY_HASH[hash]
    else:
        raise ValueError("The hash %s is not unique." % hash)


def lookup_image_by_slug(slug):
    if not slug in NON_UNIQUE_SLUGS:
        return IMAGES_BY_SLUG[slug]
    else:
        raise ValueError("The slug %s is not unique." % slug)
