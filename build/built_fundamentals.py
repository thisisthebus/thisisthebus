from thisisthebus.settings.constants import DATA_DIR
from thisisthesitebuilder.daily_log.build import process_summaries
from thisisthesitebuilder.images.build import MultimediaCollection
from thisisthesitebuilder.images.models import Image, Clip
from thisisthesitebuilder.where.build import process_locations, process_places

print("================  BUILDING FUNDAMENTALS  ================")

SUMMARIES = process_summaries()
PLACES = process_places()
LOCATIONS = process_locations(PLACES)



print("-------------  Processing Multimedia  -------------")
IMAGES = MultimediaCollection(data_dir="%s/authored/images" % DATA_DIR, multimedia_class=Image)
CLIPS = MultimediaCollection(data_dir="%s/authored/clips" % DATA_DIR, multimedia_class=Clip)

INTERTWINED_MEDIA = MultimediaCollection.intertwine(IMAGES, CLIPS)

