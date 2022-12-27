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


def format_salesdata():
    """
    analyze_customers
    """

    print("running format_salesdata")

    tasks = [0, 1, 2]
    if 0 in tasks: list_unique_rough()
    if 1 in tasks: list_unique_customers()
    if 2 in tasks: json_sales_csv()

    print("completed format_salesdata")


def list_unique_rough():
    """
    save list csv
    """

    df = retrieve_df('salesData')
    print(df)

    for col in df.columns:

        print('col = ' + str(col))

        ref_list = list(df[str(col)])

        df_temp, json_temp = list_unique(ref_list)
        fil_dst = os.path.join(retrieve_path('unique_rough_csv'), str(col) + '.csv')
        df_temp.to_csv(fil_dst)
        fil_dst = os.path.join(retrieve_path('unique_rough_json'), str(col) + '.json')
        with open(fil_dst, "w") as f:
            json.dump(json_temp, f, indent = 4)
            f.close()


def list_unique(ref_list):
    """
    return df and json
    all unique terms and count of each
    """

    items, counts, json_items = [], [], []

    for item in ref_list:

        if item in items: continue
        items.append(item)
        count = ref_list.count(item)
        counts.append(count)

        json_temp = {}
        json_temp['name'] = item
        json_temp['count'] = count
        json_items.append(json_temp)


    df = pd.DataFrame()
    df['name'] = items
    df['count'] = counts
    df = df.sort_values('count', ascending=False)
    df = reset_df(df)

    json_temp = {}
    json_temp['item_count'] = len(json_items)
    json_temp['item'] = json_items

    return(df, json_temp)


def list_unique_customers():
    """
    save json
    convert sales data in a csv
    """

    df = retrieve_df('salesData')
    print(df)

    # get the customer list
    for fil in os.listdir(retrieve_path('unique_rough_csv')):
        if 'Customer' not in fil: continue
        fil_src = os.path.join(retrieve_path('unique_rough_csv'), fil)
        customers = list(retrieve_df(fil_src)['name'])
        continue

    # format the customer name
    format_customers = []
    for customer in customers:

        temp = format_customer_name(customer)
        format_customers.append(temp)

    # make a dataframe
    df = pd.DataFrame()
    df['name'] = customers
    df['format'] = format_customers

    unique_format_customers = list(list_unique(format_customers)[0]['name'])

    json_list, customer_found = [], []
    for format_customer in unique_format_customers:

        json_temp = {}
        json_temp['format_name'] = format_customer

        df_temp = df[df['format'] == format_customer]
        json_temp['names'] =  list(df_temp['name'])

        json_list.append(json_temp)

    json_temp = {}
    json_temp['item_count'] = len(json_list)
    json_temp['item'] = json_list

    fil_dst = os.path.join(retrieve_path('unique_customers'))
    with open(fil_dst, "w") as f:
        json.dump(json_temp, f, indent = 4)
        f.close()


def format_customer_name(customer):
    """
    return format customer name
    """

    try:
        name = customer
        if 'BioBridge Global' in name: name = 'BioBridge Global'
        if 'Mesoblast' in name: name = 'Mesoblast'
        if 'Pandorum' in name: name = 'Pandorum Technologies'
        if 'Phoenestra' in name: name = 'Phoenestra'
        if 'RN Bio' in name: name = 'RN-Bio Research'
        if 'Ronawk' in name: name = 'Ronawk'
        if 'Sentien Biotechnologies, Inc.' in name: name = 'Sentien Biotechnologies, Inc.'
        if 'U.S. Food & Drug Administration' in name: name = 'FDA'
        if 'United Therapeutics' in name: name = 'United Therapeutics'
        customer = name

    except:
        print(customer)

    format_customer = str(customer).lower()
    format_customer = format_customer.replace(', inc.', '')
    format_customer = format_customer.replace('.', '')

    if 'vcu' == format_customer: format_customer = 'virginia commonwealth university'
    if 'ucsf' == format_customer: format_customer = 'university of california san francisco'
    if 'universit\u00e9 de montr\u00e9al' == format_customer: format_customer = 'university of montreal'

    return(format_customer)


def build_dates(sale):
    """
    return sale with the date
    """
    date_split = sale['Date'].split('/')

    sale['day'] = int(float(date_split[0]))
    sale['month'] = int(float(date_split[1]))
    sale['year'] = int(float(date_split[2]))

    return(sale)


def calulcate_totals(sales_list):
    """
    return json list of years and total values
    """

    yearly_totals = {}

    years = np.arange(2014, 2023, 1)

    total_value = 0
    for year in years:

        year_value = 0
        for sale in sales_list:

            if sale['year'] != year: continue

            sale_total = str(sale['$ Sales']).replace(' ', '')
            sale_total = sale_total .replace(',', '')
            try:
                sale_total = float(sale_total)
            except:
                if '(' in sale_total:
                    sale_total = 0
                else:
                    sale_total = 0

            year_value = year_value + sale_total
            total_value = total_value + sale_total

        yearly_totals['total'] = total_value
        yearly_totals[str(year)] = year_value

    total_value = 0
    for sale in sales_list:

        amount = sale['$ Sales']

        try:
            for char in [' ', ',']:
                amount = amount.replace(char, '')
        except:
            continue

        if '(' in str(sale_total): continue

        try:
            amount = float(amount)
        except:
            continue

        sale['$ Sales Number'] = amount

        total_value  = total_value  + amount

    yearly_totals['total'] = total_value

    return(yearly_totals)


def list_products(sales_list):
    """
    return product list
    """

    products = []
    for sale in sales_list:
        product = sale['Product']
        products.append(product)

    df, json = list_unique(products)

    return(json)


def list_customer_type(sales_list):
    """

    """

    types = []

    items = list_products(sales_list)['item']

    for item in items:

        product = item['name']

        #print('product = ')
        #print(product)

        if str('Service') in str(product):
            if 'service' in types: continue
            types.append('service')
            continue

        if str('Dev') in str(product):
            if 'dev-grade' in types: continue
            types.append('dev-grade')
            continue

        if str('RUO') in str(product):
            if 'ruo' in types: continue
            types.append('ruo')
            continue

        if str('cGMP') in str(product):
            if 'cGMP' in types: continue
            types.append('cGMP')
            continue

        if str('Grant') in str(product)  or str('Cost Contribution') in str(product):
            if 'grant' in types: continue
            types.append('grant')
            continue

        if str('Deposit') in str(product):
            if 'deposit' in types: continue
            types.append('deposit')
            continue

        if str('JE') in str(product):
            if 'JE' in types: continue
            types.append('JE')
            continue

        if str('Shipping') in str(product):
            if 'shipping' in types: continue
            types.append('shipping')
            continue

        products_names = ['M2001', 'KT-', 'MSC-', 'SU-', '2001', '1001', 'C4300', 'K40105', 'M40200', 'K40106', 'C44010BM', 'K40101', 'S03003', 'S80010']
        for product_name in products_names:

            if str(product_name) not in str(product): continue
            if 'product' in types: continue

            types.append('product')
            continue

        #print('product = ' + str(product))

    #print('types = ')
    #print(types)

    #assert len(types) > 0

    types.sort()

    return(types)


def json_sales_csv():
    """
    save json
    convert sales data in a csv
    """

    total_sales = 0

    # get the customer list
    customers = retrieve_json('unique_customers')['item']

    json_list = []
    for customer in customers:

        json_temp = customer

        df_all = pd.DataFrame()
        for name in json_temp['names']:

            df = retrieve_df('salesData')
            df = df[df['Customer'] == name]
            df_all = df_all.append(df)

        #print('df_all = ')
        #print(df_all)

        sales_list = []
        for i in range(len(list(df_all['Customer']))):

            #print('i = ' + str(i))

            sale = {}
            for col in df_all.columns:

                #print('col = ' + str(col))

                ref_list = list(df_all[col])
                sale[str(col)] = ref_list [i]

            sale = build_dates(sale)

            sales_list.append(sale)

        json_temp['sales'] = sales_list
        json_temp['yearly_total'] = calulcate_totals(sales_list)
        json_temp['total_sales'] = json_temp['yearly_total']['total']
        json_temp['products'] = list_products(sales_list)
        json_temp['customer_type'] = list_customer_type(sales_list)
        json_list.append(json_temp)

        total_sales = total_sales + json_temp['total_sales']

        json_all = {}
        json_all['count_customer'] = len(json_list)
        json_all['total_sales'] = round(total_sales, 2)
        json_all['customer'] = json_list

        fil_dst = os.path.join(retrieve_path('json_salesdata'))
        with open(fil_dst, "w") as f:
            json.dump(json_all, f, indent = 4)
            f.close()
