from __future__ import print_function

import hashlib
import json

import requests
import yaml
from thisisthebus.settings.constants import DATA_DIR, FRONTEND_APPS_DIR

from thisisthebus.settings.secrets import MAPBOX_ACCESS_KEY


class Place(object):

    thumb_width = 280
    thumb_height = 220

    # def __init__(self, small_name, big_name, latitude, longitude, thumbnail_style,
    #              thumbnail_zoom, link_zoom, yaml_checksum=None, use_both_names_for_slug=False,
    #              bearing=0, pitch=0,
    #              *args, **kwargs):
    def __init__(self, place_meta, yaml_checksum):
        self.place_meta = {}
        self.place_meta['bearing'] = 0
        self.place_meta['pitch'] = 0
        self.place_meta.update(place_meta)
        self.yaml_checksum = yaml_checksum
        # self.small_name = small_name
        # self.big_name = big_name
        # self.latitude = latitude
        # self.longitude = longitude
        # self.thumbnail_style = thumbnail_style
        # self.thumbnail_zoom = thumbnail_zoom
        # self.link_zoom = link_zoom
        # self.yaml_checksum = yaml_checksum
        # self.use_both_names_for_slug = use_both_names_for_slug
        # self.bearing = bearing
        # self.pitch = pitch

        # small_name = authored_place['small_name'],
        # big_name = authored_place['big_name'],
        # latitude = authored_place['lat'],
        # longitude = authored_place['lon'],
        # pitch = authored_place.get('PITCH', 0),
        # bearing = authored_place.get('BEARING', 0),
        # thumbnail_style = authored_place['thumb_style'],
        # thumbnail_zoom = authored_place['thumb_zoom'],
        # link_zoom = authored_place['link_zoom'],
        # yaml_checksum = checksum,
        # use_both_names_for_slug = authored_place['use_both_names_for_slug']

    @staticmethod
    def from_yaml(place_name):
        with open("%s/authored/places/%s" % (DATA_DIR, place_name), "r") as f:
            authored_place = yaml.load(f)
            f.seek(0)
            checksum = hashlib.md5(bytes(f.read(), encoding='utf-8')).hexdigest()

        place = Place(authored_place, yaml_checksum=checksum)

        place.small_link = authored_place.get('small_link')

        return place

    def to_slug(self):
        slug = self.place_meta['small_name'].replace(" ", "-").lower()

        if self.place_meta['use_both_names_for_slug']:
            slug += self.place_meta['big_name'].replace(" ", "-").replace(",", "").lower()

        return slug

    def filename(self):
        return "%s/compiled/places/%s" % (DATA_DIR, self.to_slug())

    def compiled_is_current(self):
        '''
        Looks at the compiled JSON version.  If checksum matches, returns the JSON representation.  Otherwise, False.
        '''
        try:
            with open("%s/compiled/places/%s" % (DATA_DIR, self.to_slug()), 'r') as f:
                json_representation = json.loads(f.read())
                checksum = json_representation.get('yaml_checksum')
                if checksum == self.yaml_checksum:
                    return json_representation
                else:
                    print("{big_name} - {small_name} is out of date.".format(**self.place_meta))
                    return False
        except FileNotFoundError:
            print("New Place: {small_name}. - {big_name}".format(**self.place_meta))
            return False

    def compile(self, force_update=False):
        '''
        Grabs mapbox image, compiles uri, and writes JSON to data/compiled/places/{{place name}}
       '''
        if force_update:
            current_place_meta = False
        else:
            current_place_meta = self.compiled_is_current()
        if current_place_meta:
            return current_place_meta, False
        else:
            print("Compiling {small_name} - {big_name}".format(**self.place_meta))

        thumb_uri = "https://api.mapbox.com/styles/v1/mapbox/{thumb_style}/static/pin-s-bus({lon},{lat}/{lon},{lat},{thumb_zoom},{bearing},{pitch}/{width}x{height}?access_token={access_token}".format(
            # lon=self.lon,
            # lat=self.lat,
            # style=self.thumb_style,
            # access_token=MAPBOX_ACCESS_KEY,
            # zoom=self.thumb_zoom,
            width=self.thumb_width,
            height=self.thumb_height,
            # bearing=self.bearing,
            # pitch=self.pitch,
            access_token=MAPBOX_ACCESS_KEY,
            **self.place_meta
        )

        self.map_uri = "https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={link_zoom}/{lat}/{lon}".format(
            **self.place_meta
        )

        response = requests.get(thumb_uri)

        if not response.status_code == 200:
            print(response.content)


        print("Content Type is %s" % response.headers['Content-Type'])
        self.place_meta['thumb_filename'] = "%s.%s" % (self.to_slug(), response.headers['Content-Type'].split('/')[1])
        #
        # place_meta = dict(
        #     lat=self.lat,
        #     lon=self.lon,
        #     small_name=self.small_name,
        #     big_name=self.big_name,
        #     thumb=self.thumb_image_filename,
        #     map=self.map_uri,
        #     small_link=self.small_link,
        # )



        if self.yaml_checksum:
            self.place_meta['yaml_checksum'] = self.yaml_checksum

        with open('%s/places/img/%s' % (FRONTEND_APPS_DIR, self.place_meta['thumb_filename']), 'wb') as output:
            output.write(response.content)

        with open(self.filename(), 'w') as f:
            f.write(json.dumps(self.place_meta))

        return self.place_meta, True