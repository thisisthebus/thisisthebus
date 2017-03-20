import os
from thisisthebus.settings.constants import DATA_DIR

from markdown import markdown
import yaml

def process_summaries():
    print("Processing Summaries.")
    summaries_dir = "%s/authored/daily-log-summaries" % DATA_DIR
    summary_files = os.listdir(summaries_dir)
    summary_files.sort()
    summaries = {}

    for counter, yaml_file in enumerate(summary_files):
        month = yaml_file.rstrip(".yaml")

        with open("%s/%s" % (summaries_dir, yaml_file), 'r') as f:
            month_yaml = yaml.load(f.read())
            for day, summary in month_yaml.items():
                day_string = str(day).zfill(2)
                summaries["%s-%s" % (month, day_string)] = markdown(summary)

    return summaries