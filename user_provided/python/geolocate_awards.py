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

from geolocate_pubs import lookup_openmaps
from write_geojson import disperse_geolocation
from summarize_data import df_to_json


def geolocate_awards():
    """
    list clinical trials using an MSC intervention
    """

    tasks = [0, 1]

    # write json for downloaded award info
    if 0 in tasks: json_awards()

    # write geojson for trials
    if 1 in tasks: geojson_awards()


def geojson_awards():
    """
    write geojson using json award data
    """

    fol_src = retrieve_path('json_awards')
    fol_dst = retrieve_path('geojson_awards')

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        fil_name = 'geojson_' + fil.split('.')[0]
        fil_dst = os.path.join(fol_dst, fil_name + '.js')

        features = []

        for award in retrieve_json(fil_src)['awards']:


            feature = {}
            feature['type'] = 'Feature'

            if 'nih' in fil.lower():
                feature['properties'] = build_prop_nih(award)

            if 'nsf' in fil.lower():
                feature['properties'] = build_prop_nsf(award)

            feature['geometry'] = build_geo(award)

            features.append(feature)

            geojson = {}
            geojson['type'] = 'FeatureCollection'
            #geojson['feature_count'] = len(features)
            geojson['features'] = features

            with open(fil_dst, "w+") as f:
                f.write('var ' + str(fil_name) + ' = ' + '\n')
                json.dump(geojson, f, indent = 6)
                f.write(';')
                f.close()


def build_prop_nsf(award):
    """
    return prop
    """

    prop = {}
    prop['awardType'] = award['awardType']
    prop['title'] = award['Title']
    prop['url'] = award['url']
    prop['program'] = award['Program(s)']
    prop['year'] = int(award['StartDate'].split('/')[-1])
    prop['aff'] = award['Organization']
    prop['cost'] = str(award['AwardedAmountToDate'])
    prop['color'] = random_color()
    prop['opacity'] = 0.5
    prop['radius'] = 5
    prop['zindex'] = int(500 - float(prop['radius']))
    prop['paneName'] = str('pane' + str(prop['zindex']).zfill(3))

    return(prop)


def build_geo(award):
    """
    return geo
    """

    try:
        lat = float(award['Latitude'])
        lon = float(award['Longitude'])

    except:
        address = str(award['Organization'] + ', '+ award['OrganizationCity'] + ', ' + award['OrganizationState'])

        address_json = {}
        address_json['name'] = address
        address_json['name_edit'] = address
        located_aff = lookup_openmaps(address_json)

        lat = float(located_aff['lat'])
        lon = float(located_aff['lon'])



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


def build_prop_nih(award):
    """
    return prop
    """

    prop = {}
    prop['title'] = award['Project Title']
    prop['awardType'] = award['awardType']
    #prop['url'] = str('https://clinicaltrials.gov/ct2/show/' + str(trial['NCTId'][0]))
    prop['year'] = float(award['Fiscal Year'])
    prop['aff'] = award['Organization Name']
    prop['cost'] = str('$' + str(award['Total Cost']))
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

    r = int(50 + 100*random.random())
    g = int(255 - 15*random.random())
    b = int(50 + 200*random.random())

    color_str = str('rgb( ' + str(r) + ' , ' +  str(g) + ' , ' + str(b) + ' )')
    #print('color_str = ' + color_str)
    return(color_str)


def json_awards():
    """
    save .json from .csv downloaded from grant website
    """

    fol_src = retrieve_path('src_awards')
    fol_dst = retrieve_path('json_awards')

    # for each csv saved in grant folder
    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        print('fil_src = ' + str(fil_src))

        df = retrieve_df(fil_src)
        awards_json = df_to_json(df)

        awards = []
        for award in awards_json:

            print('award = ')
            if 'nih' in fil:
                award['awardType'] = 'NIH Award'

            elif 'nsf' in fil:
                award['awardType'] = 'NSF Award'
                award['url'] = str('https://nsf.gov/awardsearch/showAward?AWD_ID=' + str(int(award['AwardNumber'])))


            print(award)
            awards.append(award)

        fil_name = fil.split('.')[0]
        fil_dst = os.path.join(fol_dst, fil_name + '.json')

        awards_json = {}
        awards_json['count_awards'] = len(awards)
        awards_json['awards'] = awards

        print('awards_json.keys() = ')
        print(awards_json.keys())
        print('fil_dst = ')
        print(fil_dst)
        with open(fil_dst, "w+") as f:
            json.dump(awards_json, f, indent = 8)
            f.close()
