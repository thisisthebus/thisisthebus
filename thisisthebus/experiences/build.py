import os

from markdown import markdown
import maya
import yaml

from thisisthebus.experiences.models import Experience
from thisisthebus.settings.constants import DATA_DIR


def build_experiences(summaries, locations, iotds, places):
    experience_dir = "%s/authored/experiences" % DATA_DIR
    experience_dir_listing = os.walk(experience_dir)
    experience_files = list(experience_dir_listing)[0][2]
    experiences = []
    for experience_file in experience_files:
        experiences.append(Experience.from_yaml(experience_file))
    return sorted(experiences, key=lambda e: e.start_maya, reverse=True)
