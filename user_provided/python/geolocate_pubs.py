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


def geolocate_pubs():
    """
    analyze data
    """

    print("running geolocate_pubs")

    tasks = [0,1]

    if 0 in tasks: list_affs()
    if 1 in tasks: geolocate_affs()

    print("completed geolocate_pubs")


def list_affs():
    """
    list affiliations from pubs
    """

    fol_src = retrieve_path('meta_pubs')
    fil_dst = retrieve_path('list_affs')

    affs = []

    for fil in os.listdir(fol_src):

        fil_src = os.path.join(fol_src, fil)
        for pub in retrieve_json(fil_src)['pubs']:

            if 'affs' not in pub.keys(): continue

            for aff in pub['affs']:

                if aff in affs: continue

                affs.append(aff)
                affs.sort()

                affs_json = {}
                affs_json['count_affs'] = len(affs)
                affs_json['affs'] = affs

                with open(fil_dst, "w+") as fp:
                    json.dump(affs_json, fp, indent = 8)
                    fp.close()


def geolocate_affs():
    """
    locate affs
    """
    list_missing({'reset': 'reset'})

    fil_src = retrieve_path('list_affs')
    fil_dst = retrieve_path('locate_affs')

    affs = []

    for aff in retrieve_json(fil_src)['affs']:

        json_aff = {}
        json_aff['name'] = aff

        name_edit = replace_aff(aff)
        name_edit = remove_parens(name_edit)
        json_aff['name_edit'] = name_edit

        located_aff = lookup_openmaps(json_aff)

        for key in located_aff.keys():
            json_aff[key] = located_aff[key]

        if 'lat' not in json_aff.keys():
            list_missing(json_aff)
            continue

        affs.append(json_aff)

        json_affs = {}
        json_affs['count_aff'] = len(affs)
        json_affs['affs'] = affs

        with open(fil_dst, "w+") as fp:
            json.dump(json_affs, fp, indent = 8)
            fp.close()


def replace_aff(aff):
    """
    replace aff
    """

    if aff == 'Florida State UniversityBaltimoreMD':
        return('Florida State University, Baltimore, MD')

    if aff == 'Florida State UniversityTallahasseeFL':
        return('Florida State University, Tallahassee, FL')

    if aff == 'Ludwik Hirszfeld Institute of Immunology and Experimental Therapy':
        return('Ludwik Hirszfeld Institute, Wroclaw, Poland')

    if aff == 'MIT Media Lab, United States':
        return('MIT Media Lab, Massachusetts Institute of Technology')

    if 'Songshan Lake Materials Laboratory Dongguan' in aff:
        return('China')

    if aff == 'Institute of Food Biotechnology and Genomics NAS of Ukraine':
        return('Institute of Food Biotechnology and Genomics NAS of Ukraine, Kyiv, Ukraine')

    if aff == 'NFESFlorida State UniversityTallahasseeFL':
        return('NFES, Florida State University, Tallahassee, FL')

    if aff == 'Magneto Space':
        return('Magneto Space, San Francisco, CA')

    if aff == 'University UPO':
        return('University UPO, University Eastern Piedmont, UPO, Alessandria, Novara, Vercelli, Italy')

    if aff == 'Cell Physiology Laboratory, Institute of Biomedical ProblemsRussian Academy of SciencesMoscowRussia':
        return('Cell Physiology Laboratory, Institute of Biomedical Problems, Russian Academy of Sciences, Moscow, Russia')

    if aff == 'Department of Molecular Sciences Macquarie University North Ryde New South Wales2109 Australia':
        return('Department of Molecular Sciences, Macquarie University, New South Wales, Australia')

    if aff == 'Department of Primary Industries Elizabeth Macarthur Agricultural Institute Woodbridge Road Menangle New South Wales2568 Australia':
        return('Department of Primary Industries, Elizabeth Macarthur Agricultural Institute, New South Wales, Australia')

    if aff == 'Division of Food Sciences, The University of Nottingham, Sutton Bonington Campus, Loughborough LE12 5RD,\nUK':
        return('Division of Food Sciences, The University of Nottingham, Loughborough, United Kingdom')

    if aff == 'GSI Helmholtzzentrum f\u00fcr Schwerionenforschung, and Technische Universit\u00e4t Darmstadt':
        return('Planckstraße 1, 64291 Darmstadt, Germany')

    if aff == 'INM \u2013 Leibniz Institute for New Materials gGmbH':
        return('Campus D2 2, 66123 Saarbrücken, Germany')

    if aff == 'Colloid and Interface Chemistry':
        return('Saarland University, Germany')

    if aff == 'NuVant Systems':
        return('130 N West St, Crown Point, IN 46307')

    if aff == 'Institute of Clinical Neuroscience and Medical Psychology, Medical Faculty Heinrich\u2010Heine\u2010University  D\u00fcsseldorf Germany':
        return('Dusseldorf, Germany')

    if aff == 'Friedrich-Schiller-Universit\u00e4t Jena':
        return('Jena, Germany')

    if aff == 'Department of Molecular and Structural Biochemistry, North Carolina State University, Raleigh, U.S.A.':
        return('Department of Molecular and Structural Biochemistry, North Carolina State University, Raleigh, USA')

    if aff == 'Rensselaer Polytechnic Inst.':
        return('110 8th St, Troy, NY 12180')

    if aff == 'Research Centre for Natural Sciences':
        return('Budapest')

    if aff == 'Chinese Academy of Sciences':
        return('Chinese Academy of Sciences, Beijing, China')

    if aff == 'The Russian Federation State Research Center - Institute of Biomedical Problems of Russian Academy of Sciences':
        return('The Russian Federation State Research Center - Institute of Biomedical Problems of Russian Academy of Sciences, Moscow, Russia')

    return(aff)


def remove_parens(aff):
    """
    remove parens
    """

    if '(' not in aff: return(aff)

    i0 = aff.index('(')
    i1 = aff.index(')')
    aff_edit = str(aff[:i0] + aff[i1+1:])

    print('aff_edit = ' + str(aff_edit))

    return(aff_edit)


def openmaps_affs():
    """

    """
    located_affs = []

    json_src = retrieve_json('all_affs')
    for aff in json_src['affs']:

        aff['name_edit'] = edit_aff(aff['name'])

        response = {}

        try:
            found_json = retrieve_json('located_compiled')
            for found in found_json['affs']:
                if found['name'] == aff['name']:
                    response = found
                    continue
        except:
            print('not working')

        if response == {}: response = lookup_openmaps(aff)

        print('response = ')
        print(response)

        if 'lat' not in response.keys(): list_missing(aff)

        for key in response.keys(): aff[key] = response[key]

        located_affs.append(aff)

        located_json = {}
        located_json['count'] = len(located_affs)
        located_json['affs'] = located_affs

        # save the dictionary as json
        fil_dst = os.path.join(retrieve_path('all_located'))
        #print('fil_dst = ' + str(fil_dst))
        with open(fil_dst, "w") as fp:
            json.dump(located_json, fp, indent = 8)
            fp.close()


def query_openmaps():
    """
    create geolocated.csv
    create geolocated.json
    create locations_missing.csv
    """

    # reset the list of missing locations
    report_missing('reset')

    responses = []

    # establish locations df
    df = retrieve_df('location')

    found_locs = []
    lats = []
    lons = []

    locations = list(df['location'])
    for loc in locations:

        lat, lon, response = lookup_openmaps(loc)


        found_locs.append(str(loc))
        lats.append(lat)
        lons.append(lon)

        df_temp = pd.DataFrame()
        df_temp['location'] = found_locs
        df_temp['lat'] = lats
        df_temp['lon'] = lons
        df_temp.to_csv(retrieve_path('geolocated'))

        save_value('location geolocated count', len(list(df_temp['location'])))


        if lat == 0: report_missing(loc)

        responses.append(response)
        response_dict = {}
        response_dict['item_count'] = len(responses)
        response_dict['response'] = responses
        save_json(response_dict, 'geolocated_json')


def list_missing(aff):
    """

    """
    fil_dst = os.path.join(retrieve_path('affs_missing'))

    affs = []
    print('aff = ')
    print(aff)

    if 'reset' not in aff.keys():

        if os.path.exists(fil_dst):

            missing_affs = retrieve_json('affs_missing')
            affs = retrieve_json('affs_missing')['affs']
            affs.append(aff)

    affs_missing = {}
    affs_missing['count'] = len(affs)
    affs_missing['affs'] = affs

    with open(fil_dst, "w+") as fp:
        json.dump(affs_missing, fp, indent = 8)
        fp.close()


def lookup_openmaps(aff):
    """
    return lat and lon
    """

    loc_original = aff['name_edit']

    if ',' in loc_original:
        terms = loc_original.split(',')
    else:
        terms = [loc_original]

    for i in range(len(terms)):

        address = terms[i:]
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

            response = response[0]
            response['found_address'] = address
            response['openstreetmap_url'] = specific_url

            print('response = ')
            print(response)

            return(response)

        except:
            continue


    print('loc = ' + str(loc_original))
    terms = loc_original.split(' ')
    short_term = str(' '.join(terms[-2:]))
    print('short term = ' + str(short_term))

    address = short_term
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

        response = response[0]
        response['found_address'] = address
        response['openstreetmap_url'] = specific_url

        print('response = ')
        print(response)

        return(response)

    except:
        print('no address found.')


    response = {}
    response['openstreetmap_url'] = specific_url
    return(response)
