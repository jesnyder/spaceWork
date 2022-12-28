import datetime
import json
import math
import numpy as np
import os
import pandas as pd
import random
import re
import requests
import time

from pytrials.client import ClinicalTrials


from admin import reset_df
from admin import retrieve_df
from admin import retrieve_path
from admin import retrieve_json
from admin import save_json
from admin import save_value

from write_geojson import disperse_geolocation
from summarize_data import df_to_json


def geolocate_awards():
    """
    list clinical trials using an MSC intervention
    """

    tasks = [1]

    # write geojson for trials
    if 0 in tasks: geojson_awards()
    if 1 in tasks: json_awards()


def json_awards():
    """
    save .json from .csv downloaded from grant website
    """

    fol_src = retrieve_path('src_awards')
    fol_dst = retrieve_path('json_awards')

    # for each csv saved in grant folder
    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        df = retrieve_df(fil_src)
        awards_json = df_to_json(df)

        awards = []
        for award in awards_json:
            awards.append(award)

        fil_name = fil.split('.')[0]
        fil_dst = os.path.join(fol_dst, fil_name + '.json')

        awards_json = {}
        awards_json['count_awards'] = len(awards)
        awards_json['awards'] = awards

        with open(fil_dst, "w+") as f:
            json.dump(awards_json, f, indent = 8)
            f.close()



def geojson_awards():
    """
    write geojson for awards
    """

    fol_src = retrieve_path('src_awards')
    fil_dst = retrieve_path('geojson_awards')
    fil_name = 'geojson_awards'

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        df = retrieve_df(fil_src)
        awards_json = df_to_json(df)


    features = []

    for award in awards_json:

        print('award = ')
        print(award)

        feature = {}
        feature['type'] = 'Feature'
        feature['properties'] = build_prop(award)
        #feature['properties']['aff'] = aff
        feature['geometry'] = build_geo(award)

        features.append(feature)

        geojson = {}
        geojson['type'] = 'FeatureCollection'
        #geojson['feature_count'] = len(features)
        geojson['features'] = features


        with open(fil_dst, "w+") as f:

            """
            json.dump(geojson, f, indent = 8)
            f.close()
            """

            f.write('var ' + str(fil_name) + ' = ' + '\n')
            json.dump(geojson, f, indent = 6)
            f.write(';')
            f.close()



def build_prop(award):
    """
    return prop
    """

    prop = {}
    prop['title'] = award['Project Title']
    #prop['url'] = str('https://clinicaltrials.gov/ct2/show/' + str(trial['NCTId'][0]))
    prop['year'] = float(award['Fiscal Year'])
    prop['aff'] = award['Organization Name']
    prop['cost'] = float(award['Total Cost'])
    prop['color'] = random_color()
    prop['opacity'] = 0.5
    prop['radius'] = 5
    prop['zindex'] = int(500 - float(prop['radius']))
    prop['paneName'] = str('pane' + str(prop['zindex']).zfill(3))

    print('prop[title] = ')
    print(prop['title'])

    #print('prop[year] = ')
    #print(prop['year'])

    print('prop[aff] = ')
    print(prop['aff'])

    print('prop[cost] = ')
    print(prop['cost'])

    return(prop)



def random_color():
    """
    return rgb
    """

    r = int(10 + 50*random.random())
    g = int(255 - 50*random.random())
    b = int(60 + 100*random.random())

    color_str = str('rgb( ' + str(r) + ' , ' +  str(g) + ' , ' + str(b) + ' )')
    #print('color_str = ' + color_str)
    return(color_str)


def build_geo(award):
    """
    return geo
    """

    lat = float(award['Latitude'])
    lon = float(award['Longitude'])

    lon, lat = disperse_geolocation(lon, lat)

    geo = {}
    geo['type'] = 'Point'
    geo['coordinates'] = [ lon, lat]
    #geo['lat'] = float(loc['lat'])
    #geo['lon'] = float(loc['lon'])
    #geo['display_name'] = loc['display_name']
    #geo['found_address'] = loc['found_address']


    #geo['aff'] = aff
    return(geo)
