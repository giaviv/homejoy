
from django.conf import settings
from googlemaps import Client

from zipcoder import decorators
from zipcoder.exceptions import InvalidAddressException, MultipleResultsForAddressException, UnexpectedAPIResultsException


@decorators.singleton
class GoogleMapsWrapper(object):

    def __init__(self): # raises ValueError/NotImplementedError
        self._client = Client(settings.GOOGLE_API_KEY)

    def get_address_coords(self, address):
        res = self._client.geocode(address)
        if not res:
            raise InvalidAddressException()
        if 1 < len(res):
            raise MultipleResultsForAddressException()
        info_obj = res[0]
        try:
            return (info_obj['geometry']['location']['lng'], info_obj['geometry']['location']['lat'])
        except KeyError:
            raise UnexpectedAPIResultsException()

    def get_directions_coords(self, from_addr, to_addr):
        res = self._client.directions(from_addr, to_addr)
        return self._decode_google_polyline(res[0]['overview_polyline']['points'])

    def _decode_google_polyline(self, points):
        # adapted from https://gist.github.com/signed0/2031157
        coord_chunks = [[]]
        for char in points:
            # convert each character to decimal from ascii
            value = ord(char) - 63
            # values that have a chunk following have an extra 1 on the left
            split_after = not (value & 0x20)
            value &= 0x1F
            coord_chunks[-1].append(value)
            if split_after:
                    coord_chunks.append([])
        del coord_chunks[-1]

        coords = []
        for coord_chunk in coord_chunks:
            coord = 0
            for i, chunk in enumerate(coord_chunk):
                coord |= chunk << (i * 5)
            #there is a 1 on the right if the coord is negative
            if coord & 0x1:
                coord = ~coord #invert
            coord >>= 1
            coord /= 100000.0
            coords.append(coord)

        points = []
        prev_x = 0
        prev_y = 0
        for i in xrange(0, len(coords) - 1, 2):
            if 0 ==  coords[i] and 0 == coords[i + 1]:
                continue

            prev_x += coords[i + 1]
            prev_y += coords[i]
            points.append((round(prev_x, 6), round(prev_y, 6)))

        return points