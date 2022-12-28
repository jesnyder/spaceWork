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


from admin import make_color
from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from group_pubs import find_pubs


def query_gscholar():
    """
    analyze data
    """

    print("running query_gscholar")

    tasks = [0, 1]
    for term in list(retrieve_df('gscholar_search_terms')['term']):

        print('term = ' + term)
        if 0 in tasks: search_gscholar(term)
        if 1 in tasks: aggregate_term(term)

    print("completed query_gscholar")


def aggregate_term(term):
    """
    aggregate terms
    """

    fol_src = retrieve_path('gscholar_json_scrape')
    fol_dst = retrieve_path('gscholar_json_agg')
    fil_dst = os.path.join(fol_dst, term + '.json')
    print('fil_dst = ' + str(fil_dst))

    results = []

    for fil in os.listdir(fol_src):

        if str(term) not in str(fil): continue
        if str('.json') not in str(fil): continue

        fil_src = os.path.join(fol_src, fil)

        for pub in retrieve_json(fil_src)['results']:

            if pub in results: continue
            results.append(pub)

            pub_json = {}
            pub_json['pub_count'] = len(results)
            pub_json['pubs'] = results

    with open(fil_dst, "w+") as fp:
        json.dump(pub_json, fp, indent = 8)
        fp.close()


def search_gscholar(term):
    """
    Retrieve json year by year
    """

    fol_dst = retrieve_path('gscholar_json_scrape')

    years = np.arange(2022, 2020, -1)
    num_range = np.arange(0, 100, 1)

    for year in years:

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)

        #work_completed('begin_acquire_gscholar_json_' + str(year), 0)
        for num in num_range:

            fil_name = str(term + '_' + str(year) + '_' + str(num*10).zfill(3) + '.json')
            if fil_name  in os.listdir(fol_dst): continue
            fil_dst = os.path.join(fol_dst, fil_name )
            print('fil_dst = ' + str(fil_dst))

            print('term = ' + str(term))
            print('year = ' + str(year))
            print('start num = ' + str(num*10))

            num_str = str(num).zfill(3)
            url = 'https://scholar.google.com/scholar?'
            url = url + 'start=' + str(int(num*10))
            url = url + '&q=' + term
            #url = url + '&hl=en&as_sdt=0,5'
            url = url + '&hl=en&as_sdt=0,5'
            url = url + '&as_ylo=' + str(year)
            url = url + '&as_yhi=' + str(year)

            print('url = ')
            print(url)

            soup = retrieve_html(url)
            #print('soup = ')
            #print(soup)

            data = html_to_json(soup, year)
            #print('data = ')
            #print(data)
            if data == []: break

            json_results = {}
            json_results['results_count'] = len(data)
            json_results['results'] = data

            with open(fil_dst, "w+") as fp:
                json.dump(json_results, fp, indent = 8)
            fp.close()

            aggregate_term(term)

            # continue to next year
            if len(data) < 10: break
            #if len(data) < 10 and year != int(date.strftime("%Y")): break


def retrieve_html(url):
    """
    search gscholar
    """

    print('url = ')
    print(url)

    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    proxies = {
        'http': os.getenv('HTTP_PROXY') # or just type proxy here without os.getenv()
        }

    #time_string = retrieve_datetime()
    time.sleep(60 + 60*random.random())
    #print('Wait: ' + str(round(wait_time,2)) + ' from '  + str(time_string))

    html = requests.get(url, headers=headers, proxies=proxies).text
    soup = BeautifulSoup(html, 'lxml')
    return(soup)


def html_to_json(soup, year_given):
    """
    convert html to json and save
    """

    # Scrape just PDF links
    for pdf_link in soup.select('.gs_or_ggsm a'):
        pdf_file_link = pdf_link['href']
        print(pdf_file_link)

    # JSON data will be collected here
    data = []

    # Container where all needed data is located
    for result in soup.select('.gs_ri'):
        title = result.select_one('.gs_rt').text

        try:
            title_link = result.select_one('.gs_rt a')['href']
        except:
            title_link = ''

        publication_info = result.select_one('.gs_a').text
        snippet = result.select_one('.gs_rs').text
        cited_by = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
        related_articles = result.select_one('a:nth-child(4)')['href']

        # get the year of publication of each paper
        ref_year = year_given
        try:
            txt_year = result.find("div", class_="gs_a").text
            ref_year = re.findall('[0-9]{4}', txt_year)
            ref_year = int(float(ref_year[0]))
        except:
            ref_year = int(float(year_given))

        print('ref_year = ')
        print(ref_year)


        # get number of citations for each paper
        try:
            txt_cite = result.find("div", class_="gs_fl").find_all("a")[2].string
            citations = txt_cite.split(' ')
            citations = (citations[-1])
            citations = int(citations)
        except:
            citations = 0

        try:
            all_article_versions = result.select_one('a~ a+ .gs_nph')['href']
        except:
            all_article_versions = None

        data.append({
            'year': ref_year,
            'title': title,
            'title_link': title_link,
            'publication_info': publication_info,
            'snippet': snippet,
            'citations': citations,
            'cited_by': f'https://scholar.google.com{cited_by}',
            'related_articles': f'https://scholar.google.com{related_articles}',
            'all_article_versions': f'https://scholar.google.com{all_article_versions}',
        })

    return(data)
