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

from write_geojson import build_property


def summarize_data():
    """
    summarize data
    """

    print("running summarize_data")

    tasks = [0, 1, 2, 3]
    if 0 in tasks: word_count()
    if 1 in tasks: count_fields()
    if 2 in tasks: table_js()

    if 3 in tasks: table_pubs()

    print("completed summarize_data")


def table_pubs():
    """
    create js table of pubs
    """

    fol_src = retrieve_path('meta_pubs')
    fol_dst = retrieve_path('table_js')

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        fil_name = fil.split('.')[0].replace(' ', '')
        fil_name = fil_name.replace('-', '')
        fil_name = fil_name.replace('_', '')
        fil_dst = os.path.join(fol_dst, fil_name + '.js')

        json_list = []

        for pub in retrieve_json(fil_src)['pubs']:

            json_list.append(build_property(pub))

        with open(fil_dst, "w+") as f:
            f.write('var ' + str(fil_name) + ' = ' + '\n')

            f.write( '[' + '\n')

            for line in json_list:
                print(line)
                f.write(str(line) + ' , ' + '\n')

            f.write( ']' )
            #f.write(';')
            f.close()



def table_js():
    """
    save js
    """

    fol_src = retrieve_path('field_count')
    fol_dst = retrieve_path('table_js')

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        df = retrieve_df(fil_src)

        json_list = df_to_json(df)

        fil_name = fil.split('.')[0]
        fil_name = fil_name.replace('-', '')
        fil_name = fil_name.replace('_', '')
        fil_name = fil_name.replace(' ', '')
        
        fil_dst = os.path.join(fol_dst, fil_name + '.js')

        with open(fil_dst, "w+") as f:
            f.write('var ' + str(fil_name) + ' = ' + '\n')

            f.write( '[' + '\n')

            for line in json_list:
                print(line)
                f.write(str(line) + ' , ' + '\n')

            f.write( ']' )
            #f.write(';')
            f.close()


def df_to_json(df):
    """

    """

    json_list = []

    for i in range(len(list(df.iloc[:,0]))):

        print('i = ' + str(i))

        json = {}

        for col in df.columns:

            print(df.loc[i, col])

            json[col] = df.loc[i, col]

        json_list.append(json)

    return(json_list)


def count_fields():
    """

    """

    fol_src = retrieve_path('meta_pubs')
    fol_dst = retrieve_path('field_count')

    keys = ['year', 'type', 'is-referenced-by-count', 'container-title', 'title', 'affs', 'authors', 'language', 'subject', 'source', 'funder']

    for key in keys:

        targets = []

        fil_dst = os.path.join(fol_dst, key + '.csv')

        for fil in os.listdir(fol_src):

            fil_src = os.path.join(fol_src, fil)
            for pub in retrieve_json(fil_src)['pubs']:

                if key not in pub.keys(): continue

                target = pub[key]

                if type(target) is list:
                    for item in target:
                        targets.append(item)

                else:
                    targets.append(target)

        audit_list(targets).to_csv(fil_dst)


def audit_list(targets):
    """
    return a df of unique items with count and percentage
    """

    unique_targets, counts, percents = [], [], []

    for target in targets:

        if target in unique_targets: continue

        count = targets.count(target)
        percent = round(100*count/len(targets), 5)

        unique_targets.append(target)
        counts.append(count)
        percents.append(percent)

    df = pd.DataFrame()
    df['word'] = unique_targets
    df['count'] = counts
    df['percent'] = percents
    df = reset_df(df.sort_values(by='count', ascending=False))
    return(df)


def word_count():
    """
    write geojson
    """

    fol_src = retrieve_path('meta_pubs')
    fil_dst = retrieve_path('word_count')
    print('fil_dst = ' + str(fil_dst))

    skip_words = list(retrieve_df('skip_words')['word'])

    words = []

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        for pub in retrieve_json(fil_src)['pubs']:

            for title in pub['title']:

                for word in title.split(' '):

                    word = word.replace(':', '')
                    word = word.lower()

                    if len(word) < 2: continue
                    if word in skip_words: continue

                    words.append(word)

    df = audit_list(words)

    df = df[df['count'] > 5]

    df.to_csv(fil_dst)
