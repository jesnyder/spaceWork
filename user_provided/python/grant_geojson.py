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

from format_salesdata import list_unique


def grant_geojson():
    """
    analyze data
    """

    print("running grant_geojson")

    tasks = [0, 1, 2]

    if 0 in tasks: json_grants()
    if 1 in tasks: summarize_located()
    if 2 in tasks: build_geojson('grant_json')
    #if 0 in tasks: summarize_located('located_salesdata')


    print("completed grant_geojson")


def json_grants():
    """

    """

    fol_src = retrieve_path('grants')

    for fil in os.listdir(fol_src ):

        fil_name = fil.split('.')[0]
        fil_name = fil_name.replace('_', '')

        fil_src = os.path.join(fol_src, fil)

        df = retrieve_df(fil_src)
        print('df = ')
        print(df)


        grants = []

        for i in range(len(list(df.iloc[:,0]))):

            grant = {}

            for col in df.columns:

                print('col = ' + str(col))

                ref_list = list(df[col])
                value = ref_list[i]

                try:
                    value = round(float(value), 0)
                except:
                    value = value

                col_name = col
                if '/' in col_name: col_name = col_name.replace('/', '')
                if ' ' in col_name: col_name = col_name.replace(' ', '_')

                grant[str(col_name)] = value

            url = 'https://reporter.nih.gov/search/yX9gz_61XE-5E_zhxHdxTg/project-details/'
            url = url + str(int(float(grant['Application_ID'])))
            grant['url'] = url
            grants.append(grant)



        json_all = {}
        json_all['count_grant'] = len(grants)
        json_all['grants'] = grants

        fil_dst = os.path.join(retrieve_path('grant_json'), str(fil_name) + '.json')
        with open(fil_dst, "w+") as f:
            json.dump(json_all, f, indent = 4)
            f.close()


def summarize_located():
    """
    summarize located
    """

    src_json = os.path.join(retrieve_path('grant_json'), str('NIH_grants') + '.json')
    grants = retrieve_json(src_json)['grants']

    for key in grants[0].keys():

        key_list = []
        for grant in grants:

            if type(grant[key]) is list: break
            if type(grant[key]) is dict: break

            key_list.append(grant[key])

        df_temp, json_temp = list_unique(key_list)

        fil_dst = os.path.join(retrieve_path('grants_unique_located_csv'), str(key) + '.csv')
        df_temp.to_csv(fil_dst)
        fil_dst = os.path.join(retrieve_path('grants_unique_located_json'), str(key) + '.json')
        with open(fil_dst, "w+") as f:
            json.dump(json_temp, f, indent = 4)
            f.close()


def build_geojson(src_json):
    """
    write geojson
    """

    src_fol = retrieve_path('grant_json')
    for fil in os.listdir(src_fol):

        fil_name = fil.split('.')[0].lower()
        fil_name = fil_name.replace('_', '')

        src_fil = os.path.join(src_fol, fil)
        grants = retrieve_json(src_fil)['grants']

        features = []
        for grant in grants:

            name = grant['Organization_Name']
            print('name = ' + str(name))

            feature = {}
            feature['type'] = 'Feature'
            feature['properties'] = make_properties(grant)
            feature['geometry'] = make_geometry(grant)

            if feature['geometry'] == 'skip': continue

            if feature['geometry']['coordinates'][0] == ' ': continue

            features.append(feature)
            geojson = {}
            geojson['type'] = 'Feature'
            geojson['features'] = features

            dst_json = os.path.join(retrieve_path('grants_js'), fil_name  + '.js')
            #print('dst_json = ' + str(dst_json))
            with open(dst_json, "w+") as f:
                f.write('var ' + ' ' + str(fil_name) + ' = ')
                json.dump(geojson, f, indent = 6)
                f.write(';')
                f.close()


def make_properties(item):
    """
    return json describing properties
    """

    prop = {}
    prop['url'] = item['url']
    prop['name'] = item['Organization_Name']
    prop['total_sales'] = item['Total_Cost']
    prop['customer_type'] = item['NIH_Spending_Categorization']
    prop['assign_to'] = item['Project_Title']
    prop['Funding_Mechanism'] =item['Funding_Mechanism']
    prop['paneName'] = 'paneNameGrant'
    prop['zindex'] = 300
    prop['years'] = [ int(item['Fiscal_Year'])]
    prop['radius'] = 10
    prop['opacity'] = 0.2
    prop['colorFill'] = make_color(item['Total_Cost'])
    prop['color'] = prop['colorFill']

    return(prop)


def make_color(value):
    """
    return rgb string
    """

    for fil in os.listdir(retrieve_path('grants_unique_located_csv')):

        if 'Total_Cost.csv' not in fil: continue
        fil_src = os.path.join(retrieve_path('grants_unique_located_csv'), fil)
        print('fil_src = ' + str(fil_src))
        df = retrieve_df(fil_src)
        values = list(df['name'])
        break

    fil_src = os.path.join(retrieve_path('grants_unique_located_csv'), 'Total_Cost.csv')
    df = retrieve_df(fil_src)
    values = list(df['name'])

    values_checked = []
    for value in values:

        try:
            value = float(value)
        except:
            continue

        values_checked.append(value)

    value_max = max(values_checked)
    value_min = min(values_checked)

    print('value = ' + str(value))
    print('value_min = ' + str(value_min))
    print('value_max = ' + str(value_max))

    norm = 1 - (value_max - value)/(value_max - value_min)
    mod = norm*255

    assert mod <= 255
    assert mod >= 0

    r = int(mod*0.4)
    g = int(mod*0.8)
    b = int(255)

    color_str = str('rgb( ' + str(r) + ' , ' +  str(g) + ' , ' + str(b) + ' )')
    return(color_str)


def make_geometry(customer):
    """
    return json describing geometry
    """

    geo = {}
    geo['type'] = 'Point'

    lon = customer['Longitude']
    lat = customer['Latitude']

    try:
        lon = float(lon)

    except:
        return("skip")

    lon, lat = disperse_geolocation(lon, lat)

    geo['coordinates'] = [lon, lat]
    return(geo)
