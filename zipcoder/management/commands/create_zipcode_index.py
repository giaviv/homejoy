
from django.conf import settings
from django.core.management.base import NoArgsCommand
import fiona
from rtree import index
from shapely.geometry import shape


class Command(NoArgsCommand):
    """Command creates the Rtree index file based on the zipcode shp file
    pointed to by the settings module. This index file is used in the views
    to achieve faster operations on the zipcode data.

    THIS COMMAND MUST BE RUN PRIOR TO RUNNING THE SERVER.

    Otherwise, no zipcode data will be used in the calculations."""
    def handle_noargs(self, **options):
        with fiona.drivers():
            with fiona.open(settings.ZIPCODES_SHP, 'r') as zipcodes_data:
                idx = index.Rtree(settings.RTREE_INDEX_FILE)
                for feature in zipcodes_data:
                    geometry = shape(feature['geometry'])
                    idx.insert(int(feature['id']), geometry.bounds)
        print 'Successfully created an Rtree index file at %s' % settings.RTREE_INDEX_FILE_NAME