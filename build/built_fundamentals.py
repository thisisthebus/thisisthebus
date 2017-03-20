from thisisthebus.where.build import process_locations, process_places
from thisisthebus.daily_log.build import process_summaries
from thisisthebus.iotd.build import process_images

summaries = process_summaries()
places = process_places()
locations = process_locations(places)
images = process_images()