
from django.shortcuts import render
import json

from zipcoder.forms import ZipCoderForm
from zipcoder.route_zipcoder import ZipCoder


def index(request):
    geoJSON = None
    zipcodes = []
    # if an address was submitted
    if 'POST' == request.method:
        form = ZipCoderForm(request.POST)
        zipcoder = ZipCoder()
        if form.is_valid():
            # get the zipcodes and geoJSON data for the route and zipcodes
            res = zipcoder.get_zipcodes_in_route(form.cleaned_data['route_from'],
                                                 form.cleaned_data['route_to'],
                                                 direct=(ZipCoderForm.DIRECT_LINE == form.cleaned_data['calc_option']))
            geoJSON = res['geoJSON']
            zipcodes = res['zipcodes']
    else:
        form = ZipCoderForm()

    return render(request, 'index.html', {'form': form,
                                          'zipcodes': zipcodes,
                                          'geoJSON_data': (json.dumps(geoJSON) if geoJSON else None)})
