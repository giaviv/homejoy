
import os
import os.path
import random
import string
import shutil

from django.conf import settings
import fiona
from rtree import index
from shapely.geometry import LineString, mapping, MultiLineString, Point, shape

from zipcoder.exceptions import IndexFileNotFoundException, UnsupportedIntersectionException
from zipcoder.decorators import singleton
from zipcoder.googlemaps_wrapper import GoogleMapsWrapper


@singleton
class ZipCoder(object):

    def __init__(self):
        if not os.path.isfile(settings.RTREE_INDEX_FILE_NAME):
            raise IndexFileNotFoundException()
        self._idx = index.Rtree(settings.RTREE_INDEX_FILE)
        self._gmaps = GoogleMapsWrapper()

    def _write_direct_route_shp(self, from_coords, to_coords):
        route = LineString([from_coords, to_coords])
        schema = {'geometry': 'LineString', 'properties': {}}
        tmp_route_dir = os.path.join(settings.TMP_DIR,
                             ''.join([random.choice(string.digits) for _i in range(16)]))
        tmp_route_shp = os.path.join(tmp_route_dir, 'route.shp')
        os.mkdir(tmp_route_dir)
        with fiona.drivers():
            with fiona.open(tmp_route_shp, 'w', 'ESRI Shapefile', schema, crs={'init': u'epsg:4269'}) as route_shp:
                route_shp.write({
                    'geometry': mapping(route),
                    'properties': {},
                })
        return tmp_route_shp

    def _write_directions_route_shp(self, from_addr, to_addr):
        directions_coords = self._gmaps.get_directions_coords(from_addr, to_addr)
        route = LineString(directions_coords)
        schema = {'geometry': 'LineString', 'properties': {}}
        tmp_route_dir = os.path.join(settings.TMP_DIR,
                             ''.join([random.choice(string.digits) for _i in range(16)]))
        tmp_route_shp = os.path.join(tmp_route_dir, 'route.shp')
        os.mkdir(tmp_route_dir)
        with fiona.drivers():
            with fiona.open(tmp_route_shp, 'w', 'ESRI Shapefile', schema, crs={'init': u'epsg:4269'}) as route_shp:
                route_shp.write({
                    'geometry': mapping(route),
                    'properties': {},
                })
        return tmp_route_shp

    def get_zipcodes_in_route(self, route_from, route_to, direct=True):

        tmp_route_shp = (self._write_direct_route_shp(route_from['coords'], route_to['coords']) if direct
                         else self._write_directions_route_shp(route_from['address'], route_to['address']))
        dists_to_zips = {}
        geoJSON = []
        with fiona.drivers():
            with fiona.open(settings.ZIPCODES_SHP, 'r') as zipcode_shp:
                with fiona.open(tmp_route_shp, 'r') as route_shp:
                    for route_feature in route_shp:
                        route_geometry = shape(route_feature['geometry'])
                        geoJSON.append({
                            'type': 'Feature',
                            'properties': {
                                'name': 'route',
                            },
                            'geometry': mapping(route_geometry),
                        })
                        geoJSON.append({
                            'type': 'Feature',
                            'properties': {
                                'name': 'start',
                            },
                            'geometry': mapping(Point(route_geometry.coords[0])),
                        })
                        geoJSON.append({
                            'type': 'Feature',
                            'properties': {
                                'name': 'end',
                            },
                            'geometry': mapping(Point(route_geometry.coords[-1])),
                        })
                        for zipcode_feature_id in list(self._idx.intersection(route_geometry.bounds)):
                            zipcode_feature = zipcode_shp[int(zipcode_feature_id)]
                            zipcode = zipcode_feature['properties']['GEOID10']
                            zipcode_geometry = shape(zipcode_feature['geometry'])
                            if zipcode_geometry.intersects(route_geometry):
                                geoJSON.append({
                                    'type': 'Feature',
                                    'properties': {
                                        'name': zipcode,
                                    },
                                    'geometry': mapping(zipcode_geometry),
                                })
                                inter = zipcode_geometry.intersection(route_geometry)
                                inter_lines = []
                                if isinstance(inter, MultiLineString):
                                    inter_lines = [line for line in inter]
                                elif isinstance(inter, LineString):
                                    inter_lines = [inter]
                                else:
                                    raise UnsupportedIntersectionException()
                                if inter_lines:
                                    for line in inter_lines:
                                        dist = min(route_geometry.project(Point(line.coords[0])),
                                                   route_geometry.project(Point(line.coords[-1])))
                                        dists_to_zips[dist] = zipcode
        # delete the tmp dir with the route shp file
        shutil.rmtree(os.path.dirname(tmp_route_shp))
        return {
            'geoJSON': geoJSON,
            'zipcodes': [dists_to_zips[key] for key in sorted(dists_to_zips.keys())]
        }