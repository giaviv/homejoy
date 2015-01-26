
from django import forms

from zipcoder.exceptions import BaseGoogleMapsException
from zipcoder.googlemaps_wrapper import GoogleMapsWrapper


class ZipCoderForm(forms.Form):
    """A view form for the addresses input and the selection of a direct
    line calculation versus the driving directions."""
    # consts
    DIRECT_LINE        = '1'
    DRIVING_DIRECTIONS = '2'
    CALC_CHOICES       = ((DIRECT_LINE, 'Direct line',), (DRIVING_DIRECTIONS, 'Driving directions',))

    route_from  = forms.CharField(label='Origin address', max_length=200, required=True)
    route_to    = forms.CharField(label='Destination address', max_length=200, required=True)
    calc_option = forms.ChoiceField(widget=forms.RadioSelect, choices=CALC_CHOICES, required=True)

    def clean_route_from(self):
        """Validates the from address by converting it to coordinates."""
        addr = self.cleaned_data['route_from']
        try:
            coords = GoogleMapsWrapper().get_address_coords(addr)
            # return both address and coords
            return {'address': addr, 'coords': coords}
        except BaseGoogleMapsException as e:
            raise forms.ValidationError(e.message)
        return addr

    def clean_route_to(self):
        """Validates the to address by converting it to coordinates."""
        addr = self.cleaned_data['route_to']
        try:
            coords = GoogleMapsWrapper().get_address_coords(addr)
            # return both address and coords
            return {'address': addr, 'coords': coords}
        except BaseGoogleMapsException as e:
            raise forms.ValidationError(e.message)
        return addr
