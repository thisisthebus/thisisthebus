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

    def __init__(self, small_name, big_name, latitude, longitude, thumbnail_style,
                 thumbnail_zoom, link_zoom, yaml_checksum=None, use_both_names_for_slug=False,
                 bearing=0, pitch=0,
                 *args, **kwargs):
        self.small_name = small_name
        self.big_name = big_name
        self.latitude = latitude
        self.longitude = longitude
        self.thumbnail_style = thumbnail_style
        self.thumbnail_zoom = thumbnail_zoom
        self.link_zoom = link_zoom
        self.yaml_checksum = yaml_checksum
        self.use_both_names_for_slug = use_both_names_for_slug
        self.bearing = bearing
        self.pitch = pitch

    @staticmethod
    def from_yaml(place_name):
        with open("%s/authored/places/%s" % (DATA_DIR, place_name), "r") as f:
            authored_place = yaml.load(f)
            f.seek(0)
            checksum = hashlib.md5(bytes(f.read(), encoding='utf-8')).hexdigest()

        place = Place(
            small_name=authored_place['SMALL_NAME'],
            big_name=authored_place['BIG_NAME'],
            latitude=authored_place['LAT'],
            longitude=authored_place['LON'],
            pitch=authored_place.get('PITCH', 0),
            thumbnail_style=authored_place['THUMB_STYLE'],
            thumbnail_zoom=authored_place['THUMB_ZOOM'],
            link_zoom=authored_place['LINK_ZOOM'],
            yaml_checksum=checksum,
            use_both_names_for_slug=authored_place['USE_BOTH_NAMES_FOR_SLUG']
        )

        place.small_link = authored_place.get('SMALL_LINK')

        return place

    def to_slug(self):
        slug = self.small_name.replace(" ", "-").lower()

        if self.use_both_names_for_slug:
            slug += self.big_name.replace(" ", "-").replace(",", "").lower()

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
                    print("%s - %s is out of date." % (self.small_name, self.big_name))
                    return False
        except FileNotFoundError:
            print("New Place: %s. - %s" % (self.small_name, self.big_name))
            return False

    def compile(self):
        '''
        Grabs mapbox image, compiles uri, and writes JSON to data/compiled/places/{{place name}}
       '''
        current_place_meta = self.compiled_is_current()
        if current_place_meta:
            return current_place_meta, False
        else:
            print("Compiling %s - %s" % (self.small_name, self.big_name))

        thumb_uri = "https://api.mapbox.com/styles/v1/mapbox/{style}/static/pin-s-bus({lon},{lat}/{lon},{lat},{zoom},{bearing},{pitch}/{width}x{height}?access_token={access_token}".format(
            lon=self.longitude,
            lat=self.latitude,
            style=self.thumbnail_style,
            access_token=MAPBOX_ACCESS_KEY,
            zoom=self.thumbnail_zoom,
            width=self.thumb_width,
            height=self.thumb_height,
            bearing=self.bearing,
            pitch=self.pitch,
        )

        self.map_uri = "https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={zoom}/{lat}/{lon}".format(
            lat=self.latitude,
            lon=self.longitude,
            zoom=self.link_zoom
        )

        response = requests.get(thumb_uri)

        if not response.status_code == 200:
            print(response.content)


        print("Content Type is %s" % response.headers['Content-Type'])
        self.thumb_image_filename = "%s.%s" % (self.to_slug(), response.headers['Content-Type'].split('/')[1])

        place_meta = dict(
            lat=self.latitude,
            lon=self.longitude,
            small_name=self.small_name,
            big_name=self.big_name,
            thumb=self.thumb_image_filename,
            map=self.map_uri,
            small_link=self.small_link,
        )

        if self.yaml_checksum:
            place_meta['yaml_checksum'] = self.yaml_checksum

        with open('%s/places/img/%s' % (FRONTEND_APPS_DIR, self.thumb_image_filename), 'wb') as output:
            output.write(response.content)

        with open(self.filename(), 'w') as f:
            f.write(json.dumps(place_meta))

        return place_meta, True