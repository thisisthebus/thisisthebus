from thisisthebus.settings.constants import DATA_DIR
from thisisthebus.daily_log.build import process_summaries
from thisisthebus.where.build import process_locations, process_places
from thisisthesitebuilder.images.build import MultimediaCollection, intertwine
from thisisthesitebuilder.images.models import Image, Clip

SUMMARIES = process_summaries()
PLACES = process_places()
LOCATIONS = process_locations(PLACES)


IMAGES = MultimediaCollection(data_dir="%s/compiled/images" % DATA_DIR, multimedia_class=Image)
CLIPS = MultimediaCollection(data_dir="%s/compiled/clips" % DATA_DIR, multimedia_class=Clip)

INTERTWINED_MEDIA = intertwine(IMAGES, CLIPS)

