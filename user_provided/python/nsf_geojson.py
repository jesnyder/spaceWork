from bs4 import BeautifulSoup
import codecs
import datetime
from datetime import datetime
import json
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

from write_geojson import disperse_geolocation


def nsf_geojson():
    """
    nsf_geojson
    """

    print("running nsf_geojson")

    tasks = [4]

    if 0 in tasks: json_src()
    if 1 in tasks: list_nsf_locations()
    if 2 in tasks: locate_addresses()
    if 3 in tasks: coregister_address()
    if 4 in tasks: write_geojson()

    print("completed nsf_geojson")


def coregister_address():
    """
    add address information to each grant
    """

    fol_src = retrieve_path('nsf_json')
    for fil in os.listdir(fol_src):

        features = []

        fil_src = os.path.join(fol_src, fil)
        grants = retrieve_json(fil_src)['grants']

        for grant in grants:

            for location in retrieve_json('nsf_located')['address']:

                keys = list(location.keys())[:5]
                if keys[0] not in grant.keys(): continue
                if location[keys[0]] != grant[keys[0]]: continue
                if location[keys[1]] != grant[keys[1]]: continue
                if location[keys[2]] != grant[keys[2]]: continue
                if location[keys[3]] != grant[keys[3]]: continue
                if location[keys[4]] != grant[keys[4]]: continue

                """
                if 'Organization' in grant.keys():
                    print('match found! for ' + str(grant['Organization']))
                if 'Company' in grant.keys():
                    print('match found! for ' + str(grant['Company']))
                """

                for key in location.keys():
                    grant[key] = location[key]
                continue

            print('grants assigned = ' + str(len(features)))

            assert 'lon' in grant.keys()
            features.append(grant)
            grant_json = {}
            grant_json['count'] = len(features)
            grant_json['grants'] = features
            continue

        # make a unique filename
        fil_name = fil.split('.')[0]

        # save the geojson as a variable matching the filename
        dst_json = os.path.join(retrieve_path('nsf_coregistered'), fil_name  + '.json')
        #print('dst_json = ' + str(dst_json))
        with open(dst_json, "w+") as f:
            json.dump(grant_json, f, indent = 6)
            f.close()


def write_geojson():
    """
    write geojson
    """

    fol_src = retrieve_path('nsf_coregistered')
    for fil in os.listdir(fol_src):

        features = []

        fil_src = os.path.join(fol_src, fil)
        grants = retrieve_json(fil_src)['grants']

        for grant in grants:

            feature = {}
            feature['type'] = 'Feature'
            feature['properties'] = make_prop(grant)
            feature['geometry'] = make_geo(grant)

            # build a dictionary of all the grants
            features.append(feature)
            geojson_json = {}
            geojson_json['type'] = 'Feature'
            geojson_json['features'] = features

            # make a unique filename
            fil_name = fil.split('.')[0]
            fil_name = fil_name.replace('-', '')
            fil_name = fil_name.replace('_', '')

            # save the geojson as a variable matching the filename
            dst_json = os.path.join(retrieve_path('nsf_geojson'), fil_name  + '.js')
            #print('dst_json = ' + str(dst_json))
            with open(dst_json, "w+") as f:
                f.write('var ' + ' ' + str(fil_name) + ' = ')
                json.dump(geojson_json, f, indent = 6)
                f.write(';')
                f.close()


def make_prop(grant):
    """
    return properties
    """

    prop = {}
    for key in grant.keys():
        prop[key] = grant[key]

    return(prop)


def make_geo(grant):
    """
    return geo json
    """

    geo = {}
    geo['type'] = 'Point'

    lat = grant['lat']
    lon = grant['lon']

    lon, lat = disperse_geolocation(lon, lat)

    geo['coordinates'] = [lon, lat]


    return(geo)


def locate_addresses():
    """
    find lat and lon of each address
    """

    addresses = retrieve_json('nsf_address')['address']

    located = []

    for address in addresses:

        address_list = []
        for key in address:

            address_list.append(address[key])

        location = lookup_openmaps(address_list)

        for key in location.keys():

            address[key] = location[key]

        assert 'lat' in address.keys()

        located.append(address)
        located_json = {}
        located_json['count'] = len(located)
        located_json['address'] = located

        # save the dictionary as json
        fil_dst = os.path.join(retrieve_path('nsf_located'))
        print('fil_dst = ' + str(fil_dst))
        with open(fil_dst, "w+") as fp:
            json.dump(located_json, fp, indent = 8)
            fp.close()


def lookup_openmaps(aff):
    """
    return lat and lon
    """

    terms = aff

    for i in range(len(terms)):

        address = terms[i:-1]
        address = str(' '.join(address))
        address = re.sub(r'[^a-zA-z0-9\s_]+', ' ', address)

        print(str(i) + ' address = ')
        print(address)

        specific_url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
        url_response = requests.get(specific_url)

        print('specific_url = ')
        print(specific_url)

        try:
            text = url_response.text
            response = json.loads(text)

            print('response = ')
            print(response)
            return(response[0])

        except:
            continue


def list_nsf_locations():
    """
    list unique locations
    """
    addresses = []
    fol_src = retrieve_path('nsf_json')
    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        grants = retrieve_json(fil_src)['grants']


        for grant in grants:

            address = {}
            if 'OrganizationState' in grant.keys():
                fields = ['Organization', 'OrganizationStreet', 'OrganizationCity', 'OrganizationState', 'OrganizationZip']
                for field in fields: address[field] = grant[field]

            if 'Company' in grant.keys():
                fields = ['Company', 'Address1', 'City', 'State', 'Zip']
                for field in fields: address[field] = grant[field]

            if address in addresses: continue
            addresses.append(address)

            address_json = {}
            address_json['count'] = len(addresses)
            address_json['address'] = addresses

            # save the dictionary as json
            fil_dst = os.path.join(retrieve_path('nsf_address'))
            #print('fil_dst = ' + str(fil_dst))
            with open(fil_dst, "w+") as fp:
                json.dump(address_json, fp, indent = 8)
                fp.close()


def json_src():
    """
    json source
    """

    fol_src = retrieve_path('nsf_src')
    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        print('fil_src = ' + str(fil_src))

        if 'csv' in fil:

            try:
                df = retrieve_df(fil_src)

            except:
                df = pd.read_csv(fil_src, encoding='latin1')

            print('df = ')
            print(df)

            grants = []
            for i in range(len(df.iloc[:,0])):

                #print('i = ' + str(i))

                grant = {}
                for col in df.columns:

                    #print('col = ' + col)

                    key = str(col).replace('/', ' ')
                    grant[key] = str(df.loc[i, col])

                    if col == 'AwardNumber':
                        grant['url'] = str('https://www.nsf.gov/awardsearch/showAward?AWD_ID=' + str(grant[key]))

                grants.append(grant)


        if '.json' in fil:
            grants = retrieve_json(fil_src)

        grants_json = {}
        grants_json['count'] = len(grants)
        grants_json['grants'] = grants

        print('grants = ')

        # save the dictionary as json
        fil_dst = os.path.join(retrieve_path('nsf_json'), fil.split('.')[0] + '.json')
        print('fil_dst = ' + str(fil_dst))
        with open(fil_dst, "w+") as fp:
            json.dump(grants_json, fp, indent = 8)
            fp.close()
