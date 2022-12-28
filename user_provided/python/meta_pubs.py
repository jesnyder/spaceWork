from bs4 import BeautifulSoup
import codecs
from crossref.restful import Works
import datetime
from datetime import datetime
import json
import math
import numpy as np
import os
import os.path
from random import random
import random
import re
import requests
import pandas as pd
import shutil
import statistics
from statistics import mean
import time


from admin import make_color
from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from group_pubs import find_pubs


def meta_pubs():
    """
    analyze data
    """

    print("running meta_pubs")

    tasks = [1]

    if 0 in tasks: crossref_titles()
    #if 0 in tasks: crossref_doi()
    if 1 in tasks: add_key()

    print("completed meta_pubs")


def add_key():
    """
    add keys
    """

    fol_src = retrieve_path('meta_pubs')
    fol_dst = fol_src

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        fil_dst = fil_src

        pubs_dst = []

        for pub in retrieve_json(fil_src)['pubs']:

            pub['authors'] = add_authors(pub)
            pub['affs'] = add_affs(pub)
            pub['funders'] = add_funder(pub)
            pubs_dst.append(pub)

            print('pub[authors] = ')
            print(pub['authors'])

        json_dst = {}
        json_dst['pub_count'] = len(pubs_dst)
        json_dst['pubs'] = pubs_dst

        with open(fil_dst, "w+") as fp:
            json.dump(json_dst, fp, indent = 8)
            fp.close()


def add_funder(pub):
    """

    """

    funders = []

    if 'funder' not in pub.keys(): return(funders)
    for funder in pub['funder']:

        funder_name = funder['name']
        if funder_name in funders: continue
        funders.append(funder_name)

    return(funders)


def add_affs(pub):
    """
    list unique affiliations for each pub
    """
    affs = []

    if 'author' not in pub.keys(): return(affs)

    for author in pub['author']:

        if 'affiliation' not in author.keys(): continue
        for affiliation in author['affiliation']:

            if 'name' not in affiliation.keys(): continue
            aff = affiliation['name']

            if aff in affs: continue
            affs.append(aff)

    return(affs)


def add_authors(pub):
    """
    list unique authors for each pub
    """

    authors = []

    if 'author' not in pub.keys(): return(authors)

    for author in pub['author']:

        if 'family' not in author.keys(): continue
        if 'given' not in author.keys(): continue

        name = str(author['family'] + ', ' + author['given'])

        if name in authors: continue
        authors.append(name)

    return(authors)


def crossref_doi(doi):
    """

    """

    works = Works()
    pub = works.doi(doi)
    print('pub = ')
    print(pub)
    return(pub)


def crossref_titles():
    """
    add crossref metadata to gscholar data
    """

    crossref_not_found({'reset': 'reset'})

    fol_src = retrieve_path('gscholar_json_agg')
    fol_dst = retrieve_path('meta_pubs')

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        fil_dst = os.path.join(fol_dst, fil)
        pubs_dst = []

        for pub in retrieve_json(fil_src)['pubs']:

            title = pub['title']

            bool_check, crossref_json = check_crossref(fil_dst, pub['title_link'])

            if bool_check == False:

                crossref_json = search_crossref(title)
                if crossref_json['crossref_success'] != 'Yes':
                    crossref_not_found(crossref_json)
                    continue

            for key in crossref_json.keys():
                pub[key] = crossref_json[key]

            pubs_dst.append(pub)
            json_dst = {}
            json_dst['pub_count'] = len(pubs_dst)
            json_dst['pubs'] = pubs_dst

            with open(fil_dst, "w+") as fp:
                json.dump(json_dst, fp, indent = 8)
                fp.close()


def check_crossref(fil_src, pub_link):
    """
    return pub json
    """

    try:
        pubs = retrieve_json(fil_src)['pubs']
    except:
        return(False, {})

    for pub in pubs:

        if pub['title_link'] != pub_link: continue
        return(True, pub)

    return(False, {})


def search_scrub(title):
    """
    convert to lowercase
    remove non number or letter characters

    """

    title = str(title)

    remove_strs = ['[HTML]', '[PDF]', '<scp>', '</scp>' , '<i>', '</i>', '[CITATION]' , '[C]' ]
    remove_strs.append('-')
    remove_strs.append('‐')

    for remove_str in remove_strs:
        if remove_str in title:
            title = title.replace(remove_str, ' ')

    title = title.replace(' & ', ' and ')
    #title = re.sub(r'[\W_]+', '', title)
    if ' ' == title[0]: title = title[1:]
    if ' ' == title[-1]: title = title[:-1]
    title = title.lower()


    """
    #

    remove_strs = ['<scp>', '</scp>', '\n', '<i>', '</i>']
    for str in remove_strs:
        if str in title: title = title.replace(str, ' ')

    #title = re.sub('[html]', '', title)
    #title = re.sub('[pdf]', '', title)
    #title = re.sub(r'[\W_]+', '', title)
    title = re.sub(' +', ' ', title)

    """

    return(title)


def match_scrub(title):
    """
    return a title without spaces
    """

    title = search_scrub(title)
    title = re.sub('[^A-Za-z0-9]', '', title)
    #title = title.lower()

    return(title)


def search_crossref(title):
    """
    return result
    """



    print('search crossref title = ')
    print(title)

    # create crossref url
    cross_ref_url = 'https://api.crossref.org/works?query.'
    title_url = cross_ref_url + 'title'
    specific_url = title_url + '=' + title.replace(' ', '+')
    print('specific_url = ')
    print(specific_url)

    url_response = requests.get(specific_url)

    pub = {}
    pub['crossref_success'] = 'No'
    pub['searc_title'] = title
    pub['searc_title_scrub'] = match_scrub(title)
    pub['url'] = specific_url
    pub['match_found'] = False


    try:
        text = url_response.text
        data = json.loads(text)

    except:
        pub['error'] = '01 data did not load from json.loads(text)'
        return(pub)

    # find the items in the crossref json
    try:
        if 'message' not in data.keys():
            pub['error'] = '02 message missing from data.keys()'
            return(pub)

    except:
        pub['error'] = '02 message missing from data.keys()'
        return(pub)

    try:
        message = data['message']
        if 'items' not in message.keys():
            pub['error'] = '03 items missing from message.keys()'
            return(pub)
    except:
        pub['error'] = '03 items missing from message.keys()'
        return(pub)

    try:
        items = message['items']
    except:
        pub['error'] = '04 no items found'
        return(pub)

    if 'author' not in items[0].keys():
        pub['error'] = '04 no author found in the first item'
        return(pub)

    found_title_first = items[0]['title'][0]
    found_title_first_scrub = match_scrub(found_title_first)

    for item in items:

        #if 'author' not in item.keys(): continue

        pub['crossref_success'] = 'Yes'
        pub['searched_title'] = title
        pub['url'] = specific_url
        pub['crossref_item_number'] = items.index(item)
        pub['doi_url'] = str('https://dx.doi.org/' + item['DOI'])
        pub['match_found'] = True

        for item_title in item['title']:

            if title.lower() == item_title.lower():
                #if len(list_affs(item)) > 0:
                for key in item.keys(): pub[key] = item[key]
                return(pub)

            target_title = match_scrub(title)
            found_title =  match_scrub(item_title)

            if target_title[:86] == found_title[:86]:
                #if len(list_affs(item)) > 0:
                for key in item.keys(): pub[key] = item[key]
                return(pub)

            if target_title == found_title[1:]:
                #if len(list_affs(item)) > 0:
                for key in item.keys(): pub[key] = item[key]
                return(pub)

    pub['crossref_success'] = 'No'
    pub['error'] = '05 title match not found'
    pub['found_title'] = found_title_first
    pub['found_title_scrub'] = found_title_first_scrub
    pub['affs_found'] = len(list_affs(items[0]))
    pub['match_found'] = False

    return(pub)


def find_hardcoded_crossref_affs(pub_src):
    """

    """

    if 'author' not in pub_src.keys(): return(pub_src)

    ref_json = retrieve_json('crossref_with_affs')

    for pub in ref_json['pubs']:


        #if 'DOI' in pub.keys(): key = 'DOI'
        #elif 'title_link' in pub.keys():
        key = 'title_link'

        print('key = ' + str(key))

        doi_src = str(pub_src[key])
        print('1 doi_src = ' + str(doi_src))

        doi_ref = str(pub[key])
        print('2 doi_ref = ' + str(doi_ref))


        if doi_src != doi_ref: continue

        if 'author' in pub.keys():
            pub_src['author'] = pub['author']
            return(pub_src)

    return(pub_src)


def list_affs(pub):
    """
    return a list of affs
    """

    affs = []
    if 'author' not in pub.keys(): return(affs)
    for author in pub['author']:
        for name in author['affiliation']:
            aff = name['name']
            if aff not in affs: affs.append(aff)

    return(affs)


def combine_affs(pub):
    """
    some affs are split across lines
    check for a keyword showing they were split
    then combine
    """

    affs = list_affs(pub)

    countries = ['Canada', 'Russia', 'USA', 'United States', 'Singapore', 'Australia', 'New Zealand', '117510 Singapore', 'University of Kansas', 'USA']

    if combine_check(affs, countries) == False: return(affs)

    j = 0
    new_affs = []

    for aff in affs:

        for country in countries:

            if aff.lower() != country.lower(): continue

            i = affs.index(aff)
            aff = ', '.join(affs[j:i+1])
            j = i+1
            new_affs.append(aff)

    assert len(new_affs) > 0

    print('affs = ')
    print(affs)
    print('new_affs = ')
    print(new_affs)

    return(new_affs)


def combine_check(affs, countries):
    """
    return true or false
    if the affs need to combined
    """

    for aff in affs:
        for country in countries:
            if aff.lower() == country.lower():
                return(True)
    return(False)


def crossref_not_found(item):
    """
    list crossref not found
    """

    missing_json = {}
    missing_json['pub_count'] = 0
    missing_json['pubs'] = []

    if 'reset' not in item.keys():

        try:
            missing_json = retrieve_json('missing_json')
        except:
            print('missing_json not found.')

        pubs = missing_json['pubs']
        if item not in pubs:
            pubs.append(item)

        missing_json['pub_count'] = len(pubs)
        missing_json['pubs'] = pubs

    fil_dst = os.path.join(retrieve_path('missing_json'))
    with open(fil_dst, "w") as fp:
        json.dump(missing_json, fp, indent = 8)
        fp.close()
