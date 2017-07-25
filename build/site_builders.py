import sys
from ensure_build_path import add_project_dir_to_path, BUILD_PATH
from thisisthesitebuilder.pages.build import PageBuilder

sys.path.append("~/git/thisisthesitebuilder")

add_project_dir_to_path()

if __name__ == "__main__":
    import django

    django.setup()


from thisisthesitebuilder.images.models import Image
Image.image_path = "apps/iotd/img"
from thisisthesitebuilder.images.templatetags.image_tags import register_image_tags
register_image_tags("images/iotd-instance.html")


from build.built_fundamentals import SUMMARIES, LOCATIONS, IMAGES, PLACES
from thisisthebus.experiences.build import EraBuilder

import json

from checksumdir import dirhash
import maya

from django.template.loader import get_template

from thisisthebus.settings.constants import FRONTEND_DIR, DATA_DIR, PYTHON_APP_DIR

SUMMARY_PREVIEW_LENGTH = 140


def build_daily_log(summaries, locations, iotds, places):
    days_of_note = set(list(summaries.keys()) + list(locations.keys()) + list(iotds.keys()))
    days_of_note = sorted(days_of_note, reverse=True)

    days = []
    for day in days_of_note:
        day_nice = day.replace('.md', "")
        this_day_meta = {}
        days.append((day_nice, this_day_meta))
        this_day_meta['summary'] = summaries.get(day, "")
        if iotds.get(day_nice):
            this_day_meta['images'] = iotds[day_nice]
        if locations.get(day_nice):
            # For now, take the first location.  TODO: Allow multiple lcoations for day.
            this_day_meta['place'] = places[min(locations[day_nice].items())[1]]

    t = get_template('daily-log-main-page.html')
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

    print("Building site...")

    latest_location_date, latest_location_dict = max(LOCATIONS.items())
    latest_location_time, latest_location = max(latest_location_dict.items())
    latest_place = PLACES[latest_location]

    hashes = get_hashes()
    build_time = maya.now().datetime(to_timezone='US/Eastern', naive=True)

    era_builder = EraBuilder(SUMMARIES, LOCATIONS, IMAGES, PLACES)

    experiences = era_builder.build_experiences("%s/authored/experiences" % DATA_DIR)
    t = get_template('experiences.html')
    d = {"experiences": experiences, "include_swipebox": True, "slicey": True, "page_name": "Our Travels",
         "sub_nav": [('/travels-by-experience.html', "By Experience", True), ('/travels.html', "By Date", False)]
         }
    experiences_html = t.render(d)

    with open("%s/travels-by-experience.html" % FRONTEND_DIR, "w+") as f:
        f.write(experiences_html)

    for experience in experiences:
        t = get_template('experiences.html')
        d = {"experiences": [experience], "include_swipebox": True, "slicey": True,
             "page_name": "Our Travels",
             "page_title": experience.name,
             "sub_nav": [('/travels-by-experience.html', "By Experience", False),
                         ('/travels.html', "By Date", False)]
             }
        experiences_html = t.render(d)

        with open("{frontend}/experiences/{slug}.html".format(frontend=FRONTEND_DIR, slug=experience.slug), "w+") as f:
            f.write(experiences_html)

    print("Rendered {count} Experiences.".format(count=len(experiences)))

    bigger_eras = era_builder.build_eras("%s/authored/eras" % DATA_DIR)

    for era in bigger_eras:
        t = get_template('era.html')
        d = {"era": era, "include_swipebox": True, "slicey": True,
             "page_name": "Our Travels",
             "page_title": era.name,
             "sub_nav": [('/travels-by-experience.html', "By Experience", False),
                         ('/travels.html', "By Date", False)]
             }
        era_html = t.render(d)


        with open("{frontend}/eras/{slug}.html".format(frontend=FRONTEND_DIR, slug=era.slug), "w+") as f:
            f.write(era_html)

    t = get_template('images/all-images.html')
    d = {"all_images": IMAGES, "include_swipebox": True, "slicey": True}
    all_images_html = t.render(d)

    with open("{frontend}/all-images.html".format(frontend=FRONTEND_DIR), "w+") as f:
        f.write(all_images_html)


    build_daily_log(SUMMARIES, LOCATIONS, IMAGES, PLACES)

    # Pages

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

    print("Done building site.")
    print("Data: %s" % hashes['data'])
    print("App: %s" % hashes['app'])
    input("....continue.")


if __name__ == "__main__":
    complete_build(django_setup=True)
