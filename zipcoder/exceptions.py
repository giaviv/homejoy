
class BaseZipCoderException(Exception):
    pass

class BaseGoogleMapsException(BaseZipCoderException):
    pass

class InvalidAddressException(BaseGoogleMapsException):
    def __init__(self, *args, **kwargs):
         super(BaseGoogleMapsException, self).__init__('Address could not be processed to coordinates',
                                                   *args, **kwargs)

class MultipleResultsForAddressException(BaseGoogleMapsException):
    def __init__(self, *args, **kwargs):
         super(BaseGoogleMapsException, self).__init__('Multiple results returned for address. Be more specific',
                                                   *args, **kwargs)

class UnexpectedAPIResultsException(BaseGoogleMapsException):
    def __init__(self, *args, **kwargs):
         super(BaseGoogleMapsException, self).__init__('Google API returned an unexpected value. Try a different address',
                                                   *args, **kwargs)

class IndexFileNotFoundException(BaseZipCoderException):
    pass

class UnsupportedIntersectionException(BaseZipCoderException):
    pass