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


def locate_customers():
    """
    locate_customers
    """

    print("running locate_customers")

    record_missing({"reset": "reset"})

    # list all sales json
    src_json = retrieve_json('json_sales_by_customer')
    sales = src_json['sales']

    all_sales = []
    all_value = 0

    for sale in sales:

        customer = sale['name']
        customer_name = check_name(customer)
        if 'skip' == customer_name:
            continue

        sale['location'] = lookup_openmaps(customer_name)

        if sale['location'] == {}:
            record_missing(sale)
            continue

        display_name_str = sale['location']['display_name']
        display_name = display_name_str.split(',')

        print('display_name = ')
        print(display_name)

        sale = identify_address(sale)

        sale['assgined_to'] = 'Nick'
        if 'United States' in str(sale['location']['display_name']):
            sale['assgined_to'] = 'Crystal'
        if 'Canada' in str(sale['location']['display_name']):
            sale['assgined_to'] = 'Crystal'

        all_value = all_value + sale['value']
        all_sales.append(sale)
        json_all = {}
        json_all['count'] = len(all_sales)
        json_all['value'] = all_value
        json_all['sales'] = all_sales

        dst_json = retrieve_path('located_sales_by_customer')
        #print('dst_json = ' + str(dst_json))
        with open(dst_json, "w") as f:
            json.dump(json_all, f, indent = 4)
        f.close()

    print("completed locate_customers")


def identify_address(sale):
    """
    identify parts of the address
    """

    sale['country'] = display_name[-1]
    sale['zipcode'] = find_zipcode(display_name)

    for i in range(len(display_name)):
        j = len(display_name) - i - 1
        ii = display_name[i]
        jj = display_name[j]

        if 'state' not in sale.keys():
            if jj != sale['country']:
                if str(jj).replace(" ", "") !=  str(sale['zipcode']).replace(" ", ""):
                    sale['state'] = jj
                    continue


        if 'county' not in sale.keys():
            if jj != sale['country']:
                if str(jj).replace(" ", "") !=  str(sale['zipcode']).replace(" ", ""):
                    if 'County' in str(jj):
                        sale['county'] = jj
                        continue

        if 'city' not in sale.keys():
            if ii != sale['country']:
                if str(ii).replace(" ", "") !=  str(sale['zipcode']).replace(" ", ""):
                    if 'county' in sale.keys():
                        if ii == sale['county']: continue

                    sale['city'] = ii
                    continue
    return(sale)


def find_zipcode(display_name):
    """
    return zipcode
    """

    for i in range(len(display_name)):

        j = len(display_name) - i - 1
        ii = display_name[i]
        jj = display_name[j]

        try:
            zipcode = int(float(jj))
            return(zipcode)
        except:
            continue

    return('')


def record_missing(sale):
    """

    """

    print('sale = ')
    print(sale)

    missing = []

    if 'reset' not in sale.keys():
        print('no reset')
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

    refs = retrieve_json('located')['name']

    for ref in refs:

        print('ref = ')
        print(ref)

        if customer != ref['value']: continue
        customer = ref['sub']
        return(customer)

    return(cutomer)


def lookup_openmaps(name):
    """
    return lat and lon
    """

    print('name = ')
    print(name)

    name = re.sub(r'[^a-zA-z0-9\s_]+', ' ', name)

    specific_url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(name) +'?format=json'
    url_response = requests.get(specific_url)

    print('specific_url = ')
    print(specific_url)

    try:
        text = url_response.text
        response = json.loads(text)

        response0 = response[0]
        response0['search_url'] = specific_url
        response0['search_name'] = name


    except:
        response0 = {}

    print('response0 = ')
    print(response0)

    return(response0)
