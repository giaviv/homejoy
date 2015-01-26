from django import forms

from zipcoder.exceptions import BaseGoogleMapsException
from zipcoder.googlemaps_wrapper import GoogleMapsWrapper


class ZipCoderForm(forms.Form):
    DIRECT_LINE = '1'
    DRIVING_DIRECTIONS = '2'
    CALC_CHOICES = ((DIRECT_LINE, 'Direct line',), (DRIVING_DIRECTIONS, 'Driving directions',))
    route_from = forms.CharField(label='Origin address', max_length=200, required=True)
    route_to = forms.CharField(label='Destination address', max_length=200, required=True)
    calc_option = forms.ChoiceField(widget=forms.RadioSelect, choices=CALC_CHOICES, required=True)

    def clean_route_from(self):
        data = self.cleaned_data['route_from']
        try:
            coords = GoogleMapsWrapper().get_address_coords(data)
            return {'address': data, 'coords': coords}
        except BaseGoogleMapsException as e:
            raise forms.ValidationError(e.message)
        return data

    def clean_route_to(self):
        data = self.cleaned_data['route_to']
        try:
            coords = GoogleMapsWrapper().get_address_coords(data)
            return {'address': data, 'coords': coords}
        except BaseGoogleMapsException as e:
            raise forms.ValidationError(e.message)
        return data