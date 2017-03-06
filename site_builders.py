import os

import yaml
from django.template.loader import get_template

from thisisthebus.daily_log.build import process_summaries
from thisisthebus.iotd.build import process_iotds
from thisisthebus.settings.constants import FRONTEND_DIR, DATA_DIR
from thisisthebus.where.build import process_locations, process_places

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.default_django_settings')

SUMMARY_PREVIEW_LENGTH = 140


def build_daily_log(summaries, locations, iotds, places):
    days_of_note = set(list(summaries.keys()) + list(locations.keys()) + list(iotds.keys()))
    days_of_note = sorted(days_of_note, reverse=True)

    days = []
    for day in days_of_note:
        day_nice = day.replace('.md', "")
        this_day_meta = {}
        days.append((day_nice, this_day_meta))
        this_day_meta['summary'] = summaries.get(day)
        if iotds.get(day_nice):
            this_day_meta['iotds'] = iotds[day_nice]
        if locations.get(day_nice):
            this_day_meta['place'] = places[locations[day_nice]['place']]

    t = get_template('daily-log-main-page.html')
    d = {"days": days, "include_swipebox": True}
    daily_log_html = t.render(d)

    with open("%s/pages/daily-log/index.html" % FRONTEND_DIR, "w+") as f:
        f.write(daily_log_html)


def build_front_page():
    t = get_template('bigger.html')
    html = t.render({})

    with open("%s/index.html" % FRONTEND_DIR, "w+") as f:
        f.write(html)


def complete_build():
    print("Building site...")
    summaries = process_summaries()
    places = process_places()
    locations = process_locations()
    iotds = process_iotds()

    # with open("%s/authored/timeframes.yaml" % DATA_DIR, "r") as f:
    #     timeframes = yaml.load(f)
    # timeframes

    build_daily_log(summaries, locations, iotds, places)
    build_front_page()

    print("Done building site.")



if __name__ == "__main__":
    import django
    django.setup()
    complete_build()
