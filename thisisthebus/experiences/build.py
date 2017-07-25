import os

import maya
import yaml
import datetime
from thisisthebus.experiences.models import Experience, Era
from thisisthebus.settings.constants import DATA_DIR
from thisisthesitebuilder.pages.parsers import parse_markdown_and_django_template
from thisisthesitebuilder.utils.yaml_loader import yaml_ordered_load


class EraBuilder(object):

    def __init__(self, summaries, locations, images, places):
        self.summaries = summaries
        self.locations = locations
        self.images = images
        self.places = places

    def era_meta_from_yaml(self, yaml_filename):
        with open(yaml_filename, 'r') as f:
            experience_dict = yaml_ordered_load(f.read())

        experience_dict['description'] = parse_markdown_and_django_template(experience_dict['description'])
        return experience_dict

    def era_from_yaml(self, yaml_filename):
        era_dict = self.era_meta_from_yaml(yaml_filename)
        slug = yaml_filename.rstrip('.yaml').split('/')[-1]
        era = Era(slug=slug, **era_dict)
        era.start_maya = maya.MayaDT.from_datetime(era.start)
        era.end_maya = maya.MayaDT.from_datetime(era.end)
        return era

    def experience_from_yaml(self, yaml_filename):
        experience_dict = self.era_meta_from_yaml(yaml_filename)

        right_most = yaml_filename.rstrip('.yaml').split('/')[-1]
        if right_most == "main":
            slug = yaml_filename.rstrip('.yaml').split('/')[-2]
        else:
            slug = right_most

        experience = Experience(slug=slug, **experience_dict)

        experience.start_day = experience.start.date()

        if not experience.end:
            experience.end = datetime.datetime.now()

        try:
            experience.end_day = experience.end.date()
        except:
            pass

        experience.start_maya = maya.MayaDT.from_datetime(experience.start)
        experience.end_maya = maya.MayaDT.from_datetime(experience.end)
        return experience

    def build_eras(self, eras_dir):
        eras_dir_listing = list(os.walk(eras_dir))
        era_files = eras_dir_listing[0][2]

        eras = []

        for era_file in era_files:
            era = self.era_from_yaml(eras_dir + "/" + era_file)
            era.absorb_happenings()
            eras.append(era)

        return sorted(eras, key=lambda e: e.start_maya, reverse=True)


    def build_experiences(self, experiences_dir):
        experience_dir_listing = list(os.walk(experiences_dir))
        experience_dirs = experience_dir_listing[0][1]
        experience_files = experience_dir_listing[0][2]

        top_level_experiences = []
        sub_experiences = []
        experiences_tree = [None, sub_experiences]

        for experience_dir in experience_dirs:
            top_level_experience = self.build_experiences(experiences_dir + "/" + experience_dir)[0]
            top_level_experiences.append(top_level_experience)

        has_subs = False
        for experience_file in experience_files:
            experience = self.experience_from_yaml(experiences_dir + "/" + experience_file)
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


        sub_experiences.sort(key=lambda e: e.start_maya)

        if has_subs:
            for sub_experience in sub_experiences:
                top_level_experience.sub_experiences.append(sub_experience)

            top_level_experience.absorb_happenings()
        for sub in sub_experiences:
            sub.apply_locations()

        return sorted(top_level_experiences, key=lambda e: e.start_maya, reverse=True)
