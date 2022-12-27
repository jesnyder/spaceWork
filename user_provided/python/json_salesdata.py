from bs4 import BeautifulSoup
import codecs
import datetime
#from datetime import datetime
import json
import math
import numpy as np
import os
from random import random
import random
import requests
import pandas as pd
import shutil
import statistics
from statistics import mean
import time


from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref


def json_salesdata():
    """
    json_salesdata
    """

    print("running json_salesdata")

    tasks = [3, 4]
    if 1 in tasks: list_unique()
    if 2 in tasks: json_sales()
    if 3 in tasks: list_unique_json('json_sales')
    if 4 in tasks: list_unique_json('located_sales_by_customer')
    if 5 in tasks: json_sales_by_customer()

    print("completed json_salesdata")


def json_sales_by_customer():
    """
    save sales by customer
    """

    # list all customer names
    for fil in os.listdir(retrieve_path('list_unique')):

        if 'name_formatted_from_json' not in fil: continue
        fil_src = os.path.join(retrieve_path('list_unique'), fil)
        customers = list(retrieve_df(fil_src)['value'])

    # list all sales json
    src_json = retrieve_json('json_sales')
    sales = src_json['sales']

    all_sales = []
    all_value = 0

    for customer in customers:

        try:
            print(str(round(customers.index(customer)/len(customers)*100, 3)) +  ' customer = ' + customer)
        except:
            print(str(round(customers.index(customer)/len(customers)*100, 3)))
            print('customer = ')
            print(customer)

        customer_sales = []
        value = 0

        for sale in sales:

            if customer != sale['name_formatted']: continue

            customer_sales.append(sale)
            value = value = + sale['Value']

            json_temp = {}
            json_temp['name'] = customer
            json_temp['count'] = len(customer_sales)
            json_temp['value'] = value
            json_temp['sales'] = customer_sales

        json_temp = yearly_values(json_temp)


        all_value = all_value + value
        all_sales.append(json_temp)
        json_all = {}
        json_all['count'] = len(all_sales)
        json_all['value'] = all_value
        json_all['sales'] = all_sales

        dst_json = retrieve_path('json_sales_by_customer')
        #print('dst_json = ' + str(dst_json))
        with open(dst_json, "w+") as f:
            json.dump(json_all, f, indent = 4)
        f.close()


def yearly_values(json_temp):
    """
    return json with yearly values tabulated
    """

    yearly_value = {}

    currentDateTime = datetime.datetime.now()
    date = currentDateTime.date()
    year = date.strftime("%Y")
    year = int(float(year))

    years = np.arange(2014, year+1, 1)

    for year in years:

        value = 0

        for sale in json_temp['sales']:

            if str(year) != str(sale['Year']): continue

            value = value + sale['Value']

        yearly_value[str(year)] = value

    json_temp['yearly_values'] = yearly_value

    return(json_temp)


def format_customer_name(name):
    """
    return name
    """

    try:
        if 'RESEARCH INSTITUTE OF THE MUHC' in name: name = 'MUHC Research Institute'
        if 'BioBridge Global' in name: name = 'BioBridge Global'
        if 'Mesoblast' in name: name = 'Mesoblast'
        if 'Pandorum' in name: name = 'Pandorum Technologies'
        if 'Phoenestra' in name: name = 'Phoenestra'
        if 'RN Bio' in name: name = 'RN-Bio Research'
        if 'Ronawk' in name: name = 'Ronawk'
        if 'Sentien Biotechnologies, Inc.' in name: name = 'Sentien Biotechnologies, Inc.'
        if 'U.S. Food & Drug Administration' in name: name = 'FDA'
        if 'United Therapeutics' in name: name = 'United Therapeutics'

        name = name.lower()
        name = name.replace(', inc.', '')
        name = name.replace('.', '')
        #name = name.replace(',', '')

    except:
        name = name

    return(name)


def json_sales():
    """
    json sales
    """

    df = retrieve_df('salesData')
    print(df)

    col_first = df.columns[0]

    sales_list = []
    total_value = 0
    for i in range(len(list(df[col_first]))):

        #print('i = ' + str(i))

        json_temp = {}
        for col in df.columns:

            if 'Report comes from Commissions' in col: continue

            #print('i = '  + str(i) + ' col = ' + str(col))

            json_temp[col] = df.at[i, col]

        json_temp['Year'] = int(float(str(json_temp['Date'].split('/')[-1])))
        json_temp['Month'] = int(float(str(json_temp['Date'].split('/')[1])))
        json_temp['Day'] = int(float(str(json_temp['Date'].split('/')[0])))

        json_temp['name_formatted'] = format_customer_name(json_temp['Customer'])

        value = json_temp['$ Sales'].replace(',', '')

        value = value.replace('-', '')
        value = value.replace(' ', '')

        #value = value.replace('(', '')
        #value = value.replace(')', '')
        #if value.isdigit() == False: value = 0

        if '(' in value:
            value = 0

        elif len(value) < 3:
            print('i = ' + str(i) + ' value = ' + str(value) + ' len(value) = ' + str(len(value)))
            value = 0


        json_temp['Value'] = round(float(str(value)), 2)
        total_value = total_value + json_temp['Value']

        #print('json_temp = ')
        #print(json_temp)

        sales_list.append(json_temp)

        #print('sales_list = ')
        #print(sales_list)

    json_all = {}
    json_all['total_value'] = total_value
    json_all['count'] = len(sales_list)
    json_all['sales'] = sales_list

    #print('json_all = ')
    #print(json_all)

    dst_json = retrieve_path('json_sales')
    #print('dst_json = ' + str(dst_json))

    with open(dst_json, "w+") as f:
        json.dump(json_all, f, indent = 4)
    f.close()


def list_unique_json(src_json):
    """

    """

    # list all sales json
    src_json = retrieve_json(src_json)
    sales = src_json['sales']

    keys = sales[0].keys()

    for key in keys:

        if key == 'location': continue
        if key == 'sale': continue
        if key == 'yearly_values': continue

        print('key = ' + str(key))

        terms = []
        for sale in sales:

            if key not in sale.keys(): continue

            term = sale[key]
            terms.append(term)

        list_all = []
        terms_unique, counts, values = [], [], []
        for term in terms:

            if term in terms_unique: continue

            terms_unique.append(term)
            counts.append(terms.count(term))
            values.append(sum_values(term, sales))


            json_temp = {}
            json_temp['value'] = term
            json_temp['sub'] = term
            json_temp['count'] = terms.count(term)
            json_temp['value'] = values
            list_all.append(json_temp)

        df = pd.DataFrame()
        df['count'] = counts
        df['value'] = terms_unique
        df['sales'] = values
        df = df.sort_values('count', ascending=False)
        df = reset_df(df)
        dst_fil = os.path.join(retrieve_path('list_unique'), str(key) + '_from_json' + '.csv')
        df.to_csv(dst_fil)

        json_temp = {}
        json_temp['count'] = len(list_all)
        json_temp['name'] = list_all
        dst_fil = os.path.join(retrieve_path('list_unique_json'), str(key) + '.json')
        #print('dst_json = ' + str(dst_json))

        with open(dst_fil, "w+") as f:
            json.dump(json_temp, f, indent = 4)
        f.close()


def sum_values(term, sales):
    """

    """

    value = 0

    if 'value' not in sales[0].keys(): return(value)

    for sale in sales:

        if sale['name'] != term: continue

        value = sale['value'] + value

    return(value)


def list_unique():
    """

    """

    df = retrieve_df('salesData')
    print(df)

    for col in df.columns:

        print('col = ' + str(col))

        values, counts = [], []
        for item in list(df[col]):

            if item in values: continue
            values.append(item)
            counts.append(list(df[col]).count(item))

            df_temp = pd.DataFrame()
            df_temp['count'] = counts
            df_temp['value'] = values
            df_temp = df_temp.sort_values('count',  ascending=False)
            df_temp = reset_df(df_temp)
            dst_fil = os.path.join(retrieve_path('list_unique'), str(col) + '.csv')
            df_temp.to_csv(dst_fil)
