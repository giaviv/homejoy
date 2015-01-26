
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
    """Class implements the core functionality of processing direction
    inputs and producing the features geoJSON and zipcodes encountered.
    Class is singleton because the Rtree index needs to load once only."""
    def __init__(self):
        # raise an exception if the index file does not exist
        if not os.path.isfile(settings.RTREE_INDEX_FILE_NAME):
            raise IndexFileNotFoundException()
        # initialize the index and the GoogleMaps wrapper
        self._idx = index.Rtree(settings.RTREE_INDEX_FILE)
        self._gmaps = GoogleMapsWrapper()

    def _get_tmp_shp_dir(self):
        """Returns a randomly generated tmp folder name. Ensures
        that the name does not belong to an existing folder."""
        tmp_route_dir = os.path.join(settings.TMP_DIR,
                                     ''.join([random.choice(string.digits) for _i in range(16)]))
        # just to be safe, even though barely any chance of duplicates
        while os.path.isfile(tmp_route_dir):
            tmp_route_dir = os.path.join(settings.TMP_DIR,
                                         ''.join([random.choice(string.digits) for _i in range(16)]))
        return tmp_route_dir

    def _write_direct_route_shp(self, from_coords, to_coords):
        """Function writes a direct route as a straight LineString shape
        to a temporary shp file and returns that temporary file's name.

        Keyword arguments:
        from_coords -- coordinates of the from address
        to_coords   -- coordinates of the to address
        """
        # create the line string with empty properties
        route = LineString([from_coords, to_coords])
        schema = {'geometry': 'LineString', 'properties': {}}
        # randomly generate a tmp directory for the route shp file
        tmp_route_dir = self._get_tmp_shp_dir()
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
        """Function calculates the directions polyline's coordinates,
        and creates a tmp shp file containing those coordinates as a
        line string. It then returns the tmp shp file name.

        Keyword arguments:
        from_coords -- coordinates of the from address
        to_coords   -- coordinates of the to address
        """
        directions_coords = self._gmaps.get_directions_coords(from_addr, to_addr)
        route = LineString(directions_coords)
        schema = {'geometry': 'LineString', 'properties': {}}
        # randomly generate a tmp directory for the route shp file
        tmp_route_dir = self._get_tmp_shp_dir()
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
        """Function returns the zipcodes encountered in the given route, in order encountered,
        as well as a geoJSON object containing the starting point, end point, route and zipcode
        shapes.

        Keyword arguments:
        route_from -- a dict containing the from address and coords
        route_to   -- a dict containing the from address and coords
        direct     -- specifies whether a direct route should be used, or driving directions
                      should be calculated."""
        # direct line vs directions use coordinates and textual addresses respectively
        tmp_route_shp = (self._write_direct_route_shp(route_from['coords'], route_to['coords']) if direct
                         else self._write_directions_route_shp(route_from['address'], route_to['address']))
        dists_to_zips = {}
        geoJSON = []
        with fiona.drivers():
            with fiona.open(settings.ZIPCODES_SHP, 'r') as zipcode_shp:
                with fiona.open(tmp_route_shp, 'r') as route_shp:
                    for route_feature in route_shp:
                        # add the route features to the geoJSON return value
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
                        # find zipcodes that intersect with our route
                        for zipcode_feature_id in list(self._idx.intersection(route_geometry.bounds)):
                            zipcode_feature = zipcode_shp[int(zipcode_feature_id)]
                            zipcode = zipcode_feature['properties']['GEOID10']
                            zipcode_geometry = shape(zipcode_feature['geometry'])
                            if zipcode_geometry.intersects(route_geometry):
                                # add the zipcode to the geoJSON as well
                                geoJSON.append({
                                    'type': 'Feature',
                                    'properties': {
                                        'name': zipcode,
                                    },
                                    'geometry': mapping(zipcode_geometry),
                                })
                                # get the intersection between the zipcode and the route.
                                # we do this to make sure we handle a MultiPolygon or simply
                                # a Polygon that is entered, exited, and then entered again.
                                inter = zipcode_geometry.intersection(route_geometry)
                                inter_lines = [] # holds the lines of intersections
                                if isinstance(inter, MultiLineString):
                                    inter_lines = [line for line in inter] # multiple lines
                                elif isinstance(inter, LineString):
                                    inter_lines = [inter] # just one line
                                else:
                                    raise UnsupportedIntersectionException()
                                # process the lines and index them by distances on the line
                                if inter_lines:
                                    for line in inter_lines:
                                        # get the minimum distance between the last and first
                                        # coordinates - we want to measure where we enter the
                                        # zipcode and index it by that distance.
                                        dist = min(route_geometry.project(Point(line.coords[0])),
                                                   route_geometry.project(Point(line.coords[-1])))
                                        dists_to_zips[dist] = zipcode
        # delete the tmp dir with the route shp file
        shutil.rmtree(os.path.dirname(tmp_route_shp))
        # sort the zipcode data based on the distance key
        return {
            'geoJSON': geoJSON,
            'zipcodes': [dists_to_zips[key] for key in sorted(dists_to_zips.keys())]
        }