from ensure_build_path import add_project_dir_to_path, BUILD_PATH

add_project_dir_to_path()

if __name__ == "__main__":
    import django

    django.setup()

from build.built_fundamentals import summaries, locations, images, places
from thisisthebus.experiences.build import build_experiences
from thisisthebus.pages.build import build_page

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

    # with open("%s/authored/timeframes.yaml" % DATA_DIR, "r") as f:
    #     timeframes = yaml.load(f)
    # timeframes

    latest_location_date, latest_location_dict = max(locations.items())
    latest_location_time, latest_location = max(latest_location_dict.items())
    latest_place = places[latest_location]

    hashes = get_hashes()
    build_time = maya.now().datetime(to_timezone='US/Eastern', naive=True)

    experiences = build_experiences(summaries, locations, images, places)
    t = get_template('experiences.html')
    d = {"experiences": experiences, "include_swipebox": True, "slicey": True, "page_name": "Our Travels",
         "sub_nav": [('/travels-by-experience.html', "By Experience", True), ('/travels.html', "By Date", False)]
         }
    experiences_html = t.render(d)

    with open("%s/travels-by-experience.html" % FRONTEND_DIR, "w+") as f:
        f.write(experiences_html)

    build_daily_log(summaries, locations, images, places)
    build_page("index", root=True,
               context={'place': latest_place,
                        'update_date': latest_location_date,
                        'build_hashes': hashes,
                        'build_time': build_time}
               )

    build_page("about", root=True, slicey=True)
    build_page("our-tech-stack", root=True, slicey=True)

    with open("%s/last_build.json" % BUILD_PATH, "w") as f:
        f.write(json.dumps(hashes))

    print("Done building site.")
    print("Data: %s" % hashes['data'])
    print("App: %s" % hashes['app'])
    input("....continue.")


if __name__ == "__main__":
    complete_build(django_setup=True)
