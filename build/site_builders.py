import sys

from ensure_build_path import add_project_dir_to_path, BUILD_PATH

sys.path.append("../../thisisthesitebuilder")

add_project_dir_to_path()

if __name__ == "__main__":
    import django
    django.setup()


from thisisthesitebuilder.experiences.build import EraBuilder
from thisisthesitebuilder.pages.build import PageBuilder
from thisisthesitebuilder.images.templatetags.multimedia_tags import register_image_tags
from thisisthesitebuilder.images.models import Image, Multimedia, Clip
from thisisthesitebuilder.experiences.models import Eras
# Set multimedia storage and template values.
Multimedia.set_storage_url_path("apps/multimedia")
Image.set_instance_template("images/image-instance.html")
Clip.set_instance_template("images/clip-instance.html")

from build.built_fundamentals import SUMMARIES, LOCATIONS, IMAGES, CLIPS, PLACES, INTERTWINED_MEDIA
register_image_tags("images/image-instance.html", media_collection=INTERTWINED_MEDIA)

import json

from checksumdir import dirhash
import maya

from django.template.loader import get_template

from thisisthebus.settings.constants import FRONTEND_DIR, DATA_DIR, PYTHON_APP_DIR

SUMMARY_PREVIEW_LENGTH = 140
PAGINATE_ON_MEDIA_COUNT = 75


def build_daily_log(summaries, locations, images, clips, places):
    days_of_note = set(list(summaries.keys()) + list(locations.keys()) + list(images.by_date().keys()))
    days_of_note = sorted(days_of_note, reverse=True)

    days = []
    for day in days_of_note:
        day_nice = day.replace('.md', "")
        this_day_meta = {}
        days.append((day_nice, this_day_meta))
        this_day_meta['summary'] = summaries.get(day, "")
        if images.by_date().get(day_nice):
            this_day_meta['images'] = images.by_date()[day_nice]
        if locations.get(day_nice):
            # For now, take the first location.  TODO: Allow multiple lcoations for day.
            first_location_of_day = min(locations[day_nice].items())[1]
            this_day_meta['place'] = first_location_of_day.place

    t = get_template('daily/daily-log-main-page.html')
    d = {"days": days, "include_swipebox": True, "slicey": True, "page_name": "Our Travels",
         "sub_nav": [('/travels-by-experience.html', "By Experience", False), ('/travels.html', "By Date", True)]}
    daily_log_html = t.render(d)

    with open("%s/travels.html" % FRONTEND_DIR, "w+") as f:
        f.write(daily_log_html)


def get_hashes():
    data_hash = dirhash(DATA_DIR, 'md5')
    app_hash = dirhash(PYTHON_APP_DIR, 'md5')
    hashes = {"data": data_hash,
              "app": app_hash}

    return hashes


def complete_build(django_setup=False):
    if django_setup:
        import django
        django.setup()

    print("\n====================  BUILDING SITE  ====================\n")

    latest_location_date, latest_location_dict = max(LOCATIONS.items())
    latest_location_time, latest_location = max(latest_location_dict.items())
    latest_place = latest_location.place

    hashes = get_hashes()
    build_time = maya.now().datetime(to_timezone='US/Eastern', naive=True)

    print("-------------  Building Eras and Experiences  -------------")

    era_builder = EraBuilder(SUMMARIES, LOCATIONS, IMAGES, PLACES)
    experiences = era_builder.build_experiences("%s/authored/experiences" % DATA_DIR)


    unused_images = [image for image in IMAGES if not image.is_used]
    if unused_images:
        print("***{} Images are unused***".format(len(unused_images)))

    unused_clips = [clip for clip in CLIPS if not clip.is_used]
    if unused_clips:
        print("***{} Clips are unused***".format(len(unused_clips)))


    unused_locations = []
    for location_days in LOCATIONS.values():
        for location in location_days.values():
            if not location.used_in_experiences:
                unused_locations.append(location)

    if unused_locations:
        unused_locations.sort(key=lambda l: l.__str__())
        print("*** {} Locations are unused. ***".format(len(unused_locations)))

    for location in unused_locations:
        print("***{} is unused***".format(location))

    # Paginate experiences.
    cummulative_media_count = 0
    experience_pages = Eras(page_name="experiences")

    for experience in experiences:
        if cummulative_media_count > PAGINATE_ON_MEDIA_COUNT:
            experience_pages.next_group()
            cummulative_media_count = 0
        experience_pages.add_to_group(experience)
        images, clips = experience.media_count()
        cummulative_media_count += images + (clips * 5)

    for group in experience_pages:
        html_output_file = "{path}/{filename}.html".format(path=FRONTEND_DIR, filename=experience_pages.output_filename_for_group(group))
        previous_group, previous_page = experience_pages.output_filename_and_previous_group(group)
        next_group, next_page = experience_pages.output_filename_and_next_group(group)

        previous_path = "/{filename}.html".format(filename=previous_page) if previous_group else None
        next_path = "/{filename}.html".format(filename=next_page) if next_group else None

        t = get_template('experiences/experiences.html')
        d = {"experiences": group, "include_swipebox": True, "slicey": True, "page_name": "Our Travels",
             "sub_nav": [('/experiences.html', "By Experience", True), ('/travels.html', "By Date", False)],
             "next_page": next_path, "previous_page": previous_path,
             }
        experiences_html = t.render(d)
        with open(html_output_file, "w+") as f:
            f.write(experiences_html)

    # Individual experience pages

    for experience in experiences:
        t = get_template('experiences/experiences.html')
        d = {"experiences": [experience], "include_swipebox": True, "slicey": True,
             "page_name": "Our Travels",
             "page_title": experience.name,
             "sub_nav": [('/experiences.html', "By Experience", False),
                         ('/travels.html', "By Date", False)]
             }
        experiences_html = t.render(d)

        with open("{frontend}/experiences/{slug}.html".format(frontend=FRONTEND_DIR, slug=experience.slug), "w+") as f:
            f.write(experiences_html)

    print("Rendered {count} Experiences.".format(count=len(experiences)))

    bigger_eras = era_builder.build_eras("%s/authored/eras" % DATA_DIR, experiences=experiences)

    for era in bigger_eras:
        t = get_template('experiences/era.html')
        d = {"era": era, "include_swipebox": True, "slicey": True,
             "page_name": "Our Travels",
             "page_title": era.name,
             "sub_nav": [('/experiences.html', "By Experience", False),
                         ('/travels.html', "By Date", False)]
             }
        era_html = t.render(d)

        with open("{frontend}/eras/{slug}.html".format(frontend=FRONTEND_DIR, slug=era.slug), "w+") as f:
            f.write(era_html)

    t = get_template('images/all-images.html')
    d = {"all_images": INTERTWINED_MEDIA, "include_swipebox": True, "slicey": True}
    all_images_html = t.render(d)

    with open("{frontend}/all-images.html".format(frontend=FRONTEND_DIR), "w+") as f:
        f.write(all_images_html)


    build_daily_log(SUMMARIES, LOCATIONS, IMAGES, CLIPS, PLACES)

    print("-------------  Building Pages  -------------")

    page_builder = PageBuilder(DATA_DIR, FRONTEND_DIR)

    pages = []

    pages.append(page_builder.build_page("index", root=True,
               context={'place': latest_place,
                        'update_date': latest_location_date,
                        'build_hashes': hashes,
                        'build_time': build_time}
               ))

    pages.append(page_builder.build_page("about", root=True, slicey=True))
    pages.append(page_builder.build_page("our-tech-stack", root=True, slicey=True))
    pages.append(page_builder.build_page("4th-amendment-missing", slicey=True))


    with open("%s/last_build.json" % BUILD_PATH, "w") as f:
        f.write(json.dumps(hashes))

    print("\n=====================  DONE  ========================")
    print("Data: %s" % hashes['data'])
    print("App: %s" % hashes['app'])
    print("=====================================================")
    print("Everything went, you know, OK.")


if __name__ == "__main__":
    complete_build(django_setup=True)
