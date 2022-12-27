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


def analyze_customers():
    """
    analyze_customers
    """

    print("running analyze_customers")

    tasks = [1]
    if 1 in tasks: xlsx_sum()

    print("completed analyze_customers")


def xlsx_sum():
    """
    xlsx_sum
    """

    df = pd.DataFrame()

    customers = retrieve_json('located_sales_by_customer')['sales']

    for customer in customers:

        df_temp = pd.DataFrame()

        df_temp['assigned_to'] = [customer['assgined_to']]
        df_temp['name'] = [customer['sales'][0]['Customer']]

        df_temp['rough_address'] = [customer['location']['display_name'] ]
        df_temp['rough_lat'] = [customer['location']['lat'] ]
        df_temp['rough_lon'] = [customer['location']['lon'] ]

        col_names = ['country', 'state', 'zipcode', 'county', 'city']
        for col_name in col_names:
            if col_name not in customer.keys(): continue
            df_temp[col_name] = [customer[col_name]]

        df_temp['total_spend'] = [customer['value']]

        for key in customer['yearly_values'].keys():
            df_temp[str(key)] = [ customer['yearly_values'][key] ]

        df = df.append(df_temp)
        df = df.sort_values('total_spend', ascending=False)
        df = reset_df(df)
        df.to_csv(retrieve_path('na_customers'))
