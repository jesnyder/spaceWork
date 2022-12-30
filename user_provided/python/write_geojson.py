from bs4 import BeautifulSoup
import codecs
import datetime
from datetime import datetime
import json
import jsonlines
import math
import numpy as np
import os
from random import random
import random
import re
import requests
import pandas as pd
import shutil
import statistics
from statistics import mean
import time
import unidecode
import urllib.request


from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from format_salesdata import list_unique


def write_geojson():
    """
    analyze data
    """

    print("running write_geojson")

    tasks = [0,1]
    if 0 in tasks: geojson()
    if 1 in tasks: disperse_geojson()

    print("completed write_geojson")


def disperse_geojson():
    """
    move points to not overlap
    """

    fol_src = retrieve_path('geojson')
    for fil in os.listdir(fol_src):

        features = []

        if '.json' not in fil: continue

        fil_src = os.path.join(fol_src, fil)
        fil_name = fil.split('.')[0].replace(' ', '_')
        fil_dst = os.path.join(fol_src, fil_name + '.js')

        for feature in retrieve_json(fil_src)['features']:

            print('feature = ')
            print(feature)

            if 'geometry' not in feature.keys(): continue
            if 'coordinates' not in feature['geometry'].keys(): continue
            lon, lat = feature['geometry']['coordinates']
            feature['geometry']['coordinates'] = disperse_geolocation(lon, lat)


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


def geojson():
    """
    write geojson
    """

    fol_src = retrieve_path('meta_pubs')
    fol_dst = retrieve_path('geojson')

    for fil in os.listdir(fol_src):

        features = []

        fil_src = os.path.join(fol_src, fil)
        fil_dst = os.path.join(fol_dst, fil)
        fil_name = fil.split('.')[0].replace(' ', '_')
        for pub in retrieve_json(fil_src)['pubs']:

            feature = {}
            feature['type'] = 'Feature'
            feature['properties'] = build_property(pub)

            if 'affs' not in pub.keys(): continue
            for aff in pub['affs']:

                feature['properties']['aff'] = aff
                feature['geometry'] = build_geometry(aff)

                if feature in features: continue
                features.append(feature)

                geojson = {}
                geojson['type'] = 'FeatureCollection'
                geojson['feature_count'] = len(features)
                geojson['features'] = features

                with open(fil_dst, "w+") as f:
                    #f.write('var ' + str(fil_name) + ' = ' + '\n')
                    json.dump(geojson, f, indent = 6)
                    #f.write(';')
                f.close()


def build_geometry(aff):
    """
    return geomerty
    """

    fil_src = retrieve_path('locate_affs')

    for loc in retrieve_json(fil_src)['affs']:

        if aff != loc['name']: continue

        geo = {}
        geo['type'] = 'Point'
        geo['coordinates'] = [ float(loc['lon']), float(loc['lat']) ]
        #geo['lat'] = float(loc['lat'])
        #geo['lon'] = float(loc['lon'])
        #geo['display_name'] = loc['display_name']
        #geo['found_address'] = loc['found_address']
        #geo['aff'] = aff
        return(geo)


def build_property(pub):
    """
    return property
    """

    print(pub['doi_url'])

    prop = {}
    prop['title'] = pub['title'][0]
    prop['url'] = pub['doi_url']

    try:
        prop['journal'] = pub['container-title']
    except:
        prop['journal'] = pub['publisher']

    prop['cited'] = int(pub['is-referenced-by-count'])
    prop['radius'] = int((pub['is-referenced-by-count'] + 15))
    prop['year'] = int(pub['year'])
    prop['zindex'] = int(300 - pub['is-referenced-by-count'])
    prop['paneName'] = str('pane' + str(pub['is-referenced-by-count']).zfill(3))
    prop['color'] = random_color()
    prop['aff'] = ' '
    #prop['affs'] = pub['affs']
    #prop['authors'] = pub['authors']

    return(prop)


def random_color():
    """
    return rgb
    """

    r = int(255 - 10*random.random())
    g = int(20 + 200*random.random())
    b = int(20 + 50*random.random())

    color_str = str('rgb( ' + str(r) + ' , ' +  str(g) + ' , ' + str(b) + ' )')
    print('color_str = ' + color_str)
    return(color_str)


def disperse_geolocation(lon, lat):
    """
    return randomly shifted gps location
    """

    print('original lon / lat = ' + str(lon) + ' / ' + str(lat))

    try:

        random1 =  (2*random.random() - 1)/40
        random2 =  (2*random.random() - 1)/40

        #print('random1 / random2 = ' + str(random1) + ' / ' + str(random2))

        lon = float(lon) + random1
        lat = float(lat) + random2
        lon = round(float(lon), 6)
        lat = round(float(lat), 6)

        print('shifted lon / lat = ' + str(lon) + ' / ' + str(lat))

        return(lon, lat)

    except:
        return("skip")
