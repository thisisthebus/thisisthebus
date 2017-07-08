import os

from markdown import markdown
import maya
import yaml

from thisisthebus.experiences.models import Experience
from thisisthebus.settings.constants import DATA_DIR


def apply_sub_experiences(experiences):


    return experiences

def build_experiences(experience_data_dir, *args):
    experience_dir = experience_data_dir
    experience_dir_listing = list(os.walk(experience_dir))
    experience_dirs = experience_dir_listing[0][1]
    experience_files = experience_dir_listing[0][2]

    top_level_experiences = []
    sub_experiences = []
    experiences_tree = [None, sub_experiences]

    for experience_dir in experience_dirs:
        top_level_experience = build_experiences(experience_data_dir + "/" + experience_dir)[0]
        top_level_experiences.append(top_level_experience)

    has_subs = False
    for experience_file in experience_files:
        experience = Experience.from_yaml(experience_data_dir + "/" + experience_file)
        if experience_file == "main.yaml":
            has_subs = True
            top_level_experiences.append(experience)
            top_level_experience = experience
        else:
            sub_experiences.append(experience)

    if not has_subs:
        for sub in sub_experiences:
            sub.absorb_happenings()
            top_level_experiences.append(sub)


    sub_experiences.sort(key=lambda e: e.start_maya, reverse=True)

    if has_subs:
        for sub_experience in sub_experiences:
            top_level_experience.sub_experiences.append(sub_experience)

        top_level_experience.absorb_happenings()
    # for sub in sub_experiences:
    #     sub.absorb_happenings()

    return sorted(top_level_experiences, key=lambda e: e.start_maya, reverse=True)
