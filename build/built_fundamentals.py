from thisisthebus.daily_log.build import process_summaries
from thisisthebus.where.build import process_locations, process_places
from thisisthesitebuilder.images.build import process_images

SUMMARIES = process_summaries()
PLACES = process_places()
LOCATIONS = process_locations(PLACES)
IMAGES = process_images()