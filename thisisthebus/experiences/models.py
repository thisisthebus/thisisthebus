import maya
from django.db import models
from thisisthebus.settings.constants import TIMEZONE_UTC_OFFSET
from build.built_fundamentals import SUMMARIES, LOCATIONS, IMAGES, PLACES


class Era(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    slug = models.SlugField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    headline = models.TextField()

    def __init__(self, tags=None, sections=None, *args, **kwargs):
        self.sections = sections or []
        self.tags = tags or []
        self.sub_experiences = []
        self.images = []
        super(Era, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def absorb_happenings(self):
        """
        Figure out everything that happened during this experience and populate it with the appropriate metadata.
        """

        self.all_images_with_location = []
        self.all_summaries_with_location = []

        self.apply_locations()
        self.apply_images()
        self.apply_summaries()
        # self.sort_data_by_location()

    def apply_locations(self):
        self.locations = {}
        for filename, locations_for_day in LOCATIONS.items():
            day = filename.rstrip('.yaml')
            for time, place in locations_for_day.items():
                location_maya = maya.parse(day + "T" + time)
                if self.start_maya <= location_maya <= self.end_maya:
                    # The dates match - now let's make sure that, if this is a top-level experience, that this place can be listed on it.
                    can_be_listed = not self.sub_experiences or PLACES[place].get("show_on_top_level_experience")
                    if can_be_listed:
                        # This location qualifies!  We'll make this a 2-tuple with the place as the first item and any dates as the second.
                        if not place in self.locations.keys():
                            self.locations[place] = {'place_meta': PLACES[place],
                                                              'datetimes': [], 'images': [], "summaries": []}
                        self.locations[place]['datetimes'].append(location_maya)

        # Now that we have the locations for this self, loop through them again to get start and end mayas.
        for location in self.locations.values():
            location['start'] = min(location['datetimes'])
            location['end'] = max(location['datetimes'])

        # OK, but now we want locations to be a sorted list.
        self.locations = sorted(self.locations.values(), key=lambda l: l['start'])

    def apply_images(self):
        pass

    def apply_summaries(self):
        pass




class Experience(Era):

    display = models.CharField(max_length=30)

    show_locations = models.BooleanField(default=True)
    show_dates = models.BooleanField(default=True)

    def apply_images(self):
        for day, image_list in IMAGES.items():
            for image in image_list:
                image_maya = maya.parse(day + "T" + image.time + TIMEZONE_UTC_OFFSET)
                if self.start_maya < image_maya < self.end_maya:
                    applied_to_sub = False
                    for sub_experience in self.sub_experiences:
                        for tag in sub_experience.tags:
                            if tag in image.tags:
                                sub_experience.images.append(image)
                                applied_to_sub = True
                    if not applied_to_sub:
                        self.images.append(image)

                    if self.display == "by-location":
                        # Loop through locations again, this time determining if this image goes with this location.
                        for location in self.locations:
                            if location['start'] < image_maya < location['end']:
                                location['images'].append(image)
                                self.all_images_with_location.append(image)

    def apply_summaries(self):
        # summaries
        self.summaries = {}
        for day, summary in SUMMARIES.items():
            summary_maya = maya.parse(day)
            if self.start_maya < summary_maya and summary_maya < self.end_maya:
                self.summaries[day] = summary

                # If we're doing by-location, list the summaries that way.
                if self.display == "by-location":
                    # Loop through locations again, this time determining if this image goes with this location.
                    for location in self.locations:
                        if location['start'] < summary_maya < location['end']:
                            location['summaries'].append(summary)
                            self.all_summaries_with_location.append(SUMMARIES)

    # def sort_data_by_location(self):
    #     if self.display == "by-location":
    #     # Check to be sure that all images and summaries were assigned to a location.
    #         for image in self.images:
    #             if image not in self.all_images_with_location:
    #                 print("WARNING: No associated location for %s %s - %s." % (image['day'], image['time'], image['caption']))
    #
    #         for date, summary in self.summaries.items():
    #             if date not in self.all_summaries_with_location:
    #                 print("WARNING: No associated location for summary: %s" % summary)
    #
