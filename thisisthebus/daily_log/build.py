import os
import sys

from thisisthebus.settings.constants import DATA_DIR

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from markdown import markdown


def process_summaries():
    summaries_dir = "%s/authored/daily-log-summaries" % DATA_DIR
    summary_files = os.listdir(summaries_dir)
    summary_files.sort()
    summaries = {}

    for counter, summary_day in enumerate(summary_files):
        if counter == 0:
            # This is the earliest summary.
            previous = None
        with open("%s/%s" % (summaries_dir, summary_day), 'r') as f:
            summary_html = markdown(f.read())

        try:
            subsequent_day = summary_files[counter + 1]
        except IndexError:
            subsequent_day = None
        summaries[summary_day.replace('.md', '')] = {"previous": previous, "subsequent": subsequent_day, 'text': summary_html}

        previous = summary_day

    return summaries