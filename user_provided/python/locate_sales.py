from bs4 import BeautifulSoup
import codecs
import datetime
from datetime import datetime
import json
from langdetect import detect
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
from translate import Translator
import unidecode
import urllib.request


from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref


def locate_sales():
    """
    locate_customers
    """

    print("running locate_sales")

    tasks = [0]

    if 0 in tasks: assign_locations()

    print("completed locate_sales")


def assign_locations():
    """
    assign locations
    """

    all_value = 0
    all_sales = []

    record_missing({"reset": "reset"})

    customers = retrieve_json('json_salesdata')['customer']

    for customer in customers:

        name = customer['format_name']
        print('name = ' + str(name))

        customer_name = check_name(name)
        if customer_name == 'skip':
            record_missing(customer)
            continue

        customer['location'] = lookup_openmaps(customer_name)
        if 'lon' not in customer['location'].keys():
            record_missing(customer)
            continue

        customer = identify_address(customer)

        all_value = all_value + customer['total_sales']
        all_sales.append(customer)
        json_all = {}
        json_all['count'] = len(all_sales)
        json_all['total_value'] = all_value
        json_all['customer'] = all_sales


        dst_json = retrieve_path('located_salesdata')
        #print('dst_json = ' + str(dst_json))
        with open(dst_json, "w") as f:
            json.dump(json_all, f, indent = 4)
        f.close()


def translating(text):
    """
    return English
    """

    text0 = text

    """
    try:
        lang = detect(text)
        if lang == 'en': return(text)
        translator= Translator(from_lang=lang,to_lang='en')
        translation = translator.translate(text)
        return(translation)

    except:
        print('translation failed for: ' + str(text))
        return(text0)
    """

    return(text0)


def find_country(display_name):
    """
    return country
    """
    country = display_name[-1]
    country = translating(country)

    print('country identified: ' + str(country))

    return(country)


def find_zipcode(display_name):
    """
    return zipcode
    """

    for i in range(len(display_name)):

        j = len(display_name) - i - 1
        ii = display_name[i]
        jj = str(display_name[j].replace(' ', ''))

        try:
            zipcode = int(float(jj))
            return(zipcode)
        except:
            continue

    return('')


def find_county(display_names):
    """
    return county
    """

    for display_name in display_names:

        #display_name = translating(display_name)

        if 'County' in display_name or 'Province' in display_name:

            display_name = translating(display_name)
            display_name = translating(display_name)
            print('county identified: ' + str(display_name))
            return(display_name)


def find_state(sale):
    """
    return state name
    """
    display_names = sale['location']['display_name'].split(',')

    for display_name in display_names:

        for country in retrieve_json('state_names'):

            country_name = country['name']

            if country_name not in sale['country']: continue

            for state in country['states']:

                state_name = state['name'].replace(' ', '')

                if state_name == display_name.replace(' ', ''):
                    print('state identified: ' + str(display_name))
                    return(display_name)


def find_city(sale):
    """
    return county
    """
    display_names = sale['location']['display_name'].split(',')
    for i in range(len(display_names)):

        if i < 2: continue

        j = len(display_names) - i - 1
        display_name = str(display_names[j])

        if len(display_name) < 4: continue

        print('display_name = ' + display_name)

        display_name = translating(display_name)

        if 'country' in sale.keys():
            print(sale['country'])
            if sale['country'] in display_name: continue

        if 'state' in sale.keys():
            if sale['state'] == display_name: continue

        if 'county' in sale.keys():
            if sale['county'] == display_name: continue

        if 'County' in display_name: continue

        if 'CAL Fire' in display_name: continue

        print('city found: ' + str(display_name))

        return(display_name)


def identify_address(sale):
    """
    identify parts of the address
    """

    display_name = sale['location']['display_name']
    sale['display_name'] = display_name
    display_name = translating(display_name)
    sale['translated_display_name'] = display_name

    display_names = display_name.split(', ')

    sale['country'] = find_country(display_names)
    sale['zipcode'] = find_zipcode(display_names)
    sale['state'] = find_state(sale)
    sale['county'] = find_county(display_names)
    sale['city'] = find_city(sale)

    # assign sales person based on geography
    sale['assign_to'] = 'Nick'
    if 'canada' in sale['country']: sale['assign_to'] = 'Crystal'
    if 'United States' in sale['country']: sale['assign_to'] = 'Crystal'

    return(sale)


def record_missing(sale):
    """

    """

    #print('sale = ')
    #print(sale)

    missing = []

    if 'reset' not in sale.keys():
        #print('no reset')
        missing = retrieve_json('missing_locations')['name']
        missing.append(sale)

    missing_json = {}
    missing_json['count'] = len(missing)
    missing_json['name'] = missing

    dst_json = retrieve_path('missing_locations')
    #print('dst_json = ' + str(dst_json))
    with open(dst_json, "w") as f:
        json.dump(missing_json, f, indent = 4)
    f.close()


def check_name(customer):
    """
    return name
    """

    print('customer = ' + str(customer))

    refs = retrieve_json('located')['name']

    for ref in refs:

        #print('ref = ')
        #print(ref)

        if customer != ref['value']: continue
        customer = ref['sub']
        return(customer)

    return(customer)


def lookup_openmaps(name):
    """
    return lat and lon
    """

    print('name = ')
    print(name)

    name = re.sub(r'[^a-zA-z0-9\s_]+', ' ', name)

    specific_url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(name) +'?format=json'
    url_response = requests.get(specific_url)

    #print('specific_url = ')
    #print(specific_url)

    try:
        text = url_response.text
        response = json.loads(text)

        response0 = response[0]
        response0['search_url'] = specific_url
        response0['search_name'] = name


    except:
        response0 = {}

    #print('response0 = ')
    #print(response0)

    return(response0)
