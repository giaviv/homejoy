import os.path

from django.conf import settings
from django.core.management.base import NoArgsCommand
import fiona
from rtree import index
from shapely.geometry import shape


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        with fiona.drivers():
            with fiona.open(settings.ZIPCODES_SHP, 'r') as zipcodes_data:
                idx = index.Rtree(settings.RTREE_INDEX_FILE)
                for feature in zipcodes_data:
                    geom1 = shape(feature['geometry'])
                    idx.insert(int(feature['id']), geom1.bounds)
