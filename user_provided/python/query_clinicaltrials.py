import datetime
import json
import math
import numpy as np
import os
import pandas as pd
import random
import re
import requests
import time

from pytrials.client import ClinicalTrials


from admin import reset_df
from admin import retrieve_df
from admin import retrieve_path
from admin import retrieve_json
from admin import save_json
from admin import save_value

from geolocate_pubs import lookup_openmaps


def query_clinicaltrials():
    """
    list clinical trials using an MSC intervention
    """

    tasks = [5]

    # scrape clinicalTrials.gov database
    if 0 in tasks: query_trials()

    # list unique NCTIDs
    if 1 in tasks: list_NCTId()

    # compiles into a single json file
    if 2 in tasks: coregister_fields()

    # format_search fields
    if 3 in tasks: format_data()

    # list sponsors
    if 4 in tasks: list_sponsors()

    # write geojson for trials
    if 5 in tasks: geojson_trials()


def geojson_trials():
    """
    write geojson for trials
    """

    fil_dst = retrieve_path('geojson_trials')
    fil_name = 'geojson_trials'

    features = []

    for trial in retrieve_json('scraped_trials')['trials']:


        feature = {}
        feature['type'] = 'Feature'
        feature['properties'] = build_prop(trial)
        #feature['properties']['aff'] = aff
        feature['geometry'] = build_geo(trial)

        features.append(feature)
        geojson = {}
        geojson['type'] = 'FeatureCollection'
        #geojson['feature_count'] = len(features)
        geojson['features'] = features


        with open(fil_dst, "w+") as f:
            f.write('var ' + str(fil_name) + ' = ' + '\n')
            json.dump(geojson, f, indent = 6)
            f.write(';')
            f.close()


def build_prop(trial):
    """
    return prop
    """

    prop = {}
    prop['title'] = trial['BriefTitle'][0]
    prop['url'] = str('https://clinicaltrials.gov/ct2/show/' + str(trial['NCTId'][0]))
    prop['status'] = trial['OverallStatus'][0]
    prop['aff'] = trial['LeadSponsorName'][0]
    prop['enrolled'] = trial['EnrollmentCount'][0]
    prop['color'] = random_color()
    prop['opacity'] = 0.5
    prop['radius'] = 10
    prop['zindex'] = int(400 - float(prop['radius']))
    prop['paneName'] = str('pane' + str(prop['zindex']).zfill(3))

    return(prop)


def random_color():
    """
    return rgb
    """

    r = int(100 + 100*random.random())
    g = int(10 + 50*random.random())
    b = int(255 - 50*random.random())

    color_str = str('rgb( ' + str(r) + ' , ' +  str(g) + ' , ' + str(b) + ' )')
    #print('color_str = ' + color_str)
    return(color_str)


def build_geo(trial):
    """
    return geo
    """

    aff = trial['LeadSponsorName'][0]

    print('aff = ')
    print(aff)

    fil_src = retrieve_path('located_trials')

    for loc in retrieve_json(fil_src)['sponsors']:

        print('loc = ')
        print(loc)

        if aff != loc['name']: continue

        geo = {}
        geo['type'] = 'Point'
        geo['coordinates'] = [ float(loc['lon']), float(loc['lat']) ]
        #geo['lat'] = float(loc['lat'])
        #geo['lon'] = float(loc['lon'])
        #geo['display_name'] = loc['display_name']
        #geo['found_address'] = loc['found_address']
        #geo['aff'] = aff
        return(geo)

    return(geo)


def list_sponsors():
    """
    save a list of sponsors
    """

    fil_dst = retrieve_path('located_trials')

    sponsors = []
    located_sponsors = []

    for trial in retrieve_json('scraped_trials')['trials']:

        for sponsor in trial['LeadSponsorName']:

            if sponsor in sponsors: continue
            sponsors.append(sponsor)

            print('sponsor = ')
            print(sponsor)

            try:
                city = trial['LocationCity'][0]
            except:
                city = ' '


            try:
                country = trial['LocationCountry'][0]
            except:
                country = ' '

            aff = {}
            aff['name'] = sponsor
            aff['address'] = str(sponsor + ', ' + city + ', ' + country)
            aff['name_edit'] = str(sponsor + ', ' + city + ', ' + country)

            print(aff['name_edit'])

            response = lookup_openmaps(aff)

            for key in response.keys(): aff[key] = response[key]

            assert 'lat' in aff.keys()

            print('aff = ')
            print(aff)

            located_sponsors.append(aff)

            json_sponsor = {}
            json_sponsor['count_sponsors'] = len(located_sponsors)
            json_sponsor['sponsors'] = located_sponsors

            with open(fil_dst, "w+") as fp:
                json.dump(json_sponsor, fp, indent = 8)
                fp.close()


def query_trials():
    """
    use pytrials to retrieve all trial metadata from clinicaltrials.gov
    use search terms saved in user_provided>admin folder
    use field term also saved in user_provided>admin folder
    """

    time_begin = datetime.datetime.today()
    print('begin query_trials ' + str(time_begin))

    terms = list(retrieve_df('ctrials_search_terms')['term'])
    print('terms = ')
    print(terms)

    for term in terms:
        search_term = str(term)
        print('search_term = ' + str(search_term))
        clinicaltrials_query(search_term)

    """
    for term in list(retrieve_df('allo_terms')['term']):
        search_term = str('mesenchymal ' + str(term))
        clinicaltrials_query(search_term)

    for term in list(retrieve_df('auto_terms')['term']):
        search_term = str('mesenchymal ' + str(term))
        clinicaltrials_query(search_term)
    """


def clinicaltrials_query(term):
    """
    provide search term
    return query results
    """

    field_terms = list(retrieve_json('search_fields')['StudyFields']['Fields'])
    fields =  field_terms

    print('term = ' + term)

    max_len = 15
    i = max_len
    while i < len(fields) + max_len:

        filename =  term  + ' ' + str(i).zfill(3) + '.json'
        fol_dst = os.path.join(retrieve_path('trials_found'), term)
        # create the folder, if it doesnt exist
        if os.path.exists(fol_dst) == False: os.mkdir(fol_dst)

        if filename in os.listdir(fol_dst):
            i = i + max_len
            continue

        try:
            field_trun = fields[i-max_len:i]
        except:
            continue

        if 'NCTId' not in field_trun:
            field_trun.append('NCTId')

        ct = ClinicalTrials()

        search_expression = term.replace(' ', '+')

        #results = ct.get_full_studies(search_expr=search_expression)
        # Get the NCTId, Condition and Brief title fields from 500 studies related to Coronavirus and Covid, in csv format.
        results = ct.get_study_fields(
            search_expr=search_expression,
            fields=field_trun,
            max_studies=1000,
            fmt="json",
        )

        count = results['StudyFieldsResponse']['NStudiesReturned']
        print('count = ' + str(count))

        filename =  term  + ' ' + str(i).zfill(3) + '.json'
        fol_dst = os.path.join(retrieve_path('trials_found'), term)
        # create the folder, if it doesnt exist
        if os.path.exists(fol_dst) == False: os.mkdir(fol_dst)
        fil_dst = os.path.join(fol_dst, filename)
        #print('fil_dst = ' + str(fil_dst))
        save_json(results, fil_dst )

        i = i + max_len


def clinicaltrials_nctid_query(term):
    """
    provide search term
    return query results
    """

    print('term = ' + term)

    # create the folder, if it doesnt exist
    fol_dst = os.path.join(retrieve_path('trials_json_id'))
    if os.path.exists(fol_dst) == False: os.mkdir(fol_dst)
    filename =  term  + '.json'
    fil_dst = os.path.join(fol_dst, filename)

    fields = list(retrieve_json('search_fields')['StudyFields']['Fields'])

    try:
        json = retrieve_json(fil_dst)
        if 'WhyStopped' in json.keys():
            return()
    except:
        trial_dict = {}

    trial_dict = {}

    max_len = 15
    i = max_len
    while i < len(fields) + max_len:

        field_trun = fields[i-max_len:i]

        if 'NCTId' not in field_trun:
            field_trun.append('NCTId')

        search_expression = term.replace(' ', '+')

        #results = ct.get_full_studies(search_expr=search_expression)
        # Get the NCTId, Condition and Brief title fields from 500 studies related to Coronavirus and Covid, in csv format.
        ct = ClinicalTrials()
        results = ct.get_study_fields(
            search_expr=search_expression,
            fields=field_trun,
            max_studies=1000,
            fmt="json",
        )

        count = results['StudyFieldsResponse']['NStudiesReturned']
        print('count = ' + str(count))

        #print(results)
        #assert count == 1

        for trial in results['StudyFieldsResponse']['StudyFields'][:1]:

            assert 'NCTId' in trial.keys()

            trialID = str(trial['NCTId'][0])
            filename =  trialID  + '.json'
            fil_dst = os.path.join(fol_dst, filename)

            for key in trial.keys():

                if key in trial_dict.keys():
                    continue

                trial_dict[key] = trial[key]

            print('fil_dst = ' + str(fil_dst))
            save_json(trial_dict, fil_dst )

        i = i + max_len


def list_NCTId():
    """
    list all unique nctids across all search queries
    """

    nctids = []
    src = retrieve_path('trials_found')
    for fol in os.listdir(src):

        fol_src = os.path.join(src, fol)
        #print('fol_src =' + str(fol_src))

        for fil in os.listdir(fol_src):
            fil_src = os.path.join(fol_src, fil)
            #print('fil_src =' + str(fil_src))

            results = retrieve_json(fil_src)

            if 'StudyFieldsResponse' not in results.keys():
                continue
            if 'StudyFields' not in results['StudyFieldsResponse'].keys():
                continue

            for record in results['StudyFieldsResponse']['StudyFields']:

                #print('record.keys()')
                #print(record.keys())

                num = str(record['NCTId'][0])

                if num in nctids: continue

                nctids.append(num)

                df = pd.DataFrame()
                df['nctids'] = nctids
                df = reset_df(df.sort_values(by='nctids'))
                df.to_csv(retrieve_path('nctids'))

                #print('len(nctids) = ' + str(len(nctids)))
                #save_value('NCTIds found in scraped', len(nctids))


def coregister_fields():
    """
    combine all json scraped in query
    """

    nctids = list(retrieve_df('nctids')['nctids'])

    for nctid in nctids:

        try:
            aggregate_scraped_nctid(nctid)
        except:
            clinicaltrials_nctid_query(nctid)

        jsons = []

    for fil in os.listdir(retrieve_path('trials_json_id')):

        fil_src = os.path.join(retrieve_path('trials_json_id'), fil)

        jsons.append(retrieve_json(fil_src))
        json_dict = {}
        json_dict['trial count'] = len(jsons)
        json_dict['trials'] = jsons
        print('len(jsons) = ' + str(len(jsons)))
        save_json(json_dict, 'scraped_trials')


def aggregate_scraped_nctid(nctid):
    """
    search scraped clinicaltrials info to build json for the trial
    """

    fol_dst = os.path.join(retrieve_path('trials_json_id'))
    filename =  nctid  + '.json'
    fil_dst = os.path.join(fol_dst, filename)
    try:
        test = retrieve_json(fil_dst)
        if 'WhyStopped' in test.keys(): return()
    except:
        print(fil_dst)


    # list folders found in search
    for fol in os.listdir(retrieve_path('trials_found')):

        fol_src = os.path.join(retrieve_path('trials_found'), fol)
        fil = os.listdir(fol_src)[0]
        fil_src = os.path.join(fol_src, fil)
        if fil_search(nctid, fil_src) == {}: continue

        trial_dict = {}
        for fil in os.listdir(fol_src):

            fil_src = os.path.join(fol_src, fil)
            trial = fil_search(nctid, fil_src)

            if fil_search(nctid, fil_src) == {}: continue

            for key in trial.keys():
                trial_dict[key] = trial[key]

        # save json
        save_json(trial_dict, fil_dst)
        return()


def fil_search(nctid, fil_src):
    """
    return the contents of the file
    """

    trials = retrieve_json(fil_src)

    if 'StudyFieldsResponse' not in trials.keys():
        return({})

    if 'StudyFields' not in trials['StudyFieldsResponse'].keys():
        return({})

    for trial in trials['StudyFieldsResponse']['StudyFields']:

        if nctid in trial['NCTId']: return(trial)

    return({})


def format_data():
    """
    format to fit with downloaded data
    """


    df_all = pd.DataFrame()


    trials = retrieve_json('scraped_trials')
    for trial in trials['trials']:

        df = pd.DataFrame()
        df['NCT Number'] = [str(trial['NCTId'][0])]

        if 'NCT03339973' in str(trial['NCTId'][0]): continue
        if 'NCT05165628' in str(trial['NCTId'][0]): continue

        url = str('https://ClinicalTrials.gov/show/') + str(trial['NCTId'][0])
        #print(url)

        try:
            try:
                df['Title'] = [str(trial['BriefTitle'][0])]
            except:
                df['Title'] = [str(trial['OfficialTitle'][0])]
        except:

            if 'NCT03339973' in str(trial['NCTId'][0]):
                df['Title'] = ['Allogeneic ABCB5-positive Stem Cells for Treatment of PAOD']


        df['Status'] = [' '.join(trial['OverallStatus'])]
        #print('Status = ')
        #print(df['Status'] )
        #if df['Status'] == []: df['Status'] = [' '.join(trial['LastKnownStatus'])]

        df['Conditions'] = [' '.join(trial['Condition'])]

        df['Interventions'] = [ list_intervention(trial) ]

        df['Sponsor/Collaborators'] = [' '.join(trial['LeadSponsorName'])]

        df['Locations'] = [build_address(trial)]

        df['Outcome Measures'] = [build_outcome(trial)]

        df['Gender'] =  [' '.join(trial['Gender'])]

        df['Age'] = [build_age(trial)]

        df['Phases'] = ['|'.join(trial['Phase'])]

        df['Enrollment'] = [' '.join(trial['EnrollmentCount'])]

        df['Funded Bys'] = [str(trial['LeadSponsorClass'][0])]

        try:
            df['Study Type'] = [str(trial['StudyType'][0])]
        except:
            df['Study Type'] = [str(trial['OrgClass'][0])]

        df['Study Designs'] =  [' '] #str(trial['StudyDesigns'][0])

        df['Other IDs'] = [' '] #str(trial['OtherIDs'][0])

        df['Start Date'] = [' '.join(trial['StartDate'])]

        df['Primary Completion Date'] = [' '.join(trial['PrimaryCompletionDate'])]

        df['Completion Date'] = [' '.join(trial['CompletionDate'])]

        df['First Posted'] = [str(trial['StudyFirstSubmitDate'][0])]

        df['Results First Posted'] = [' '.join(trial['ResultsFirstPostDate'])]

        df['Last Update Posted'] = [' '.join(trial['LastUpdatePostDate'])]

        df['Study Documents'] = [str(trial['OrgClass'][0])]

        df['URL'] = [str('https://ClinicalTrials.gov/show/') + str(trial['NCTId'][0])]

        df['desc'] = [ build_desc(trial)]

        df['Brief Summary'] = [str(' '.join(trial['BriefSummary']))]

        df['Brief Title'] = [' '.join(trial['BriefTitle'])]

        df['Official Title'] = [' '.join(trial['OfficialTitle'])]

        print(url)
        #assert 'mesenchymal' in list_intervention(trial).lower() or 'mesenchymal' in desc.lower()

        #print('df = ')
        #print(df)

        df_all = df_all.append(df)

        df_all = reset_df(df_all.sort_values(by='NCT Number'))
        #print('df_all = ')
        #print(df_all)
        df_all.to_csv(retrieve_path('scraped_trials_df'))


def list_intervention(trial):
    """

    """

    inter = ''
    for key in trial.keys():

        if 'Intervention' not in str(key): continue

        term = ' '.join(trial[key])

        if inter == '': inter = str(term)
        else: inter = str(inter + ' ' + term)

    inter = ' '.join(inter.splitlines())
    return(inter)


def build_desc(trial):
    """
    return description
    """

    desc = ''
    desc = desc + ' ' + ' '.join(trial['BriefTitle'])
    desc = desc + ' ' +  ' '.join(trial['OfficialTitle'])
    desc = desc + str(' '.join(trial['BriefSummary']))
    desc = desc + ' ' +   list_intervention(trial)
    #desc = str(desc + ' ' +  build_outcome(trial))
    desc = desc.lower()
    desc = ' '.join(desc.splitlines())

    return(desc)


def build_outcome(trial):
    """
    return all outcome fields compiled in a string with
    json keys included
    """


    outcome = ''
    for key in trial.keys():

        if 'Outcome' not in str(key): continue


        if outcome == '': outcome = key + ': '
        else: outcome = outcome + ' ' + key + ': '

        term = ' '.join(trial[key])
        outcome = str(outcome + ' ' + term + ' | ')

    outcome = ' '.join(outcome.splitlines())
    return(outcome)


def build_address(trial):
    """
    return list of locations
    """

    facilities = trial['LocationFacility']
    cities = trial['LocationCity']
    states = trial['LocationState']
    zips = trial['LocationZip']
    countries = trial['LocationCountry']

    #print(facilities)
    #print(cities)
    #print(states)

    assert len(cities) == len(countries)

    locations = ''
    for i in range(len(cities)):

        if locations != '': locations = locations + ' | '

        try:
            locations = locations + str(facilities[i]) + ', '
        except:
            locations = locations

        locations = locations + str(cities[i]) + ', '

        try:
            if 'Austria' in countries[i]:
                locations = locations
            if 'Moscow Region' in states[i]:
                locations = locations
            else:
                locations = locations + str(states[i]) + ', '
        except:
            locations = locations


        locations = locations + str(countries[i])

    return(locations)


def build_age(trial):
    """
    return age
    """

    minAge = trial['MinimumAge']
    maxAge = trial['MaximumAge']

    if 'Years' in minAge and 'Years' in maxAge:
        minAge = minAge.replace('Years', '')

    if trial['MaximumAge'] == [] and len(minAge) > 0:
        age = 'Over ' + str(minAge[0])

    elif len(minAge) > 0 and len(maxAge) > 0:
        age = str(minAge[0]) + ' - ' + str(maxAge[0])

    else:
        age = str(' '.join(minAge) + ' - ' + ' '.join(maxAge))
    return(age)
