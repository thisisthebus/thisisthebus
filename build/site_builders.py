from ensure_build_path import add_project_dir_to_path, BUILD_PATH

from thisisthebus.pages.build import build_page

add_project_dir_to_path()

import json

from checksumdir import dirhash
import os, sys
import maya

from django.template.loader import get_template

from thisisthebus.daily_log.build import process_summaries
from thisisthebus.iotd.build import process_iotds
from thisisthebus.settings.constants import FRONTEND_DIR, DATA_DIR, APP_DIR
from thisisthebus.where.build import process_locations, process_places

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thisisthebus.settings.default_django_settings')

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
            this_day_meta['iotds'] = iotds[day_nice]
        if locations.get(day_nice):
            this_day_meta['place'] = places[locations[day_nice]['place']]

    t = get_template('daily-log-main-page.html')
    d = {"days": days, "include_swipebox": True, "slicey": True, "page_name": "Our Travels"}
    daily_log_html = t.render(d)

    with open("%s/travels.html" % FRONTEND_DIR, "w+") as f:
        f.write(daily_log_html)


def get_hashes():
    data_hash = dirhash(DATA_DIR, 'md5')
    app_hash = dirhash(APP_DIR, 'md5')
    hashes = {"data": data_hash,
              "app": app_hash}

    return hashes


def complete_build(django_setup=False):

    if django_setup:
        import django
        django.setup()

    print("Building site...")
    summaries = process_summaries()
    places = process_places()
    locations = process_locations()
    iotds = process_iotds()

    # with open("%s/authored/timeframes.yaml" % DATA_DIR, "r") as f:
    #     timeframes = yaml.load(f)
    # timeframes

    latest_location = locations[max(locations.keys())]
    latest_location_date = latest_location['day']
    latest_location_place = places[latest_location['place']]

    hashes = get_hashes()
    build_time = maya.now().datetime(to_timezone='US/Eastern', naive=True)
    build_daily_log(summaries, locations, iotds, places)
    build_page("index", root=True, context={'place': latest_location_place, 'update_date': latest_location_date, 'build_hashes': hashes, 'build_time': build_time})
    build_page("about", root=True, slicey=True)


    with open("%s/last_build.json" % BUILD_PATH, "w") as f:
        f.write(json.dumps(hashes))

    print("Done building site.")
    print("Data: %s" % hashes['data'])
    print("App: %s" % hashes['app'])
    input("....continue.")


if __name__ == "__main__":
    complete_build(django_setup=True)
