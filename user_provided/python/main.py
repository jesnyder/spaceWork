import codecs
import datetime
from datetime import datetime
import json
import math
import numpy as np
import os
from random import random
import pandas as pd
import shutil
import statistics
from statistics import mean
import time


from admin import reset_df
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from list_pubs import list_pubs

from geolocate_affs import geolocate_affs
from group_pubs import group_pubs
from build_table import build_table
from contact_list import contact_list
from write_html import write_html

from query_gscholar import query_gscholar
from meta_pubs import meta_pubs
from geolocate_pubs import geolocate_pubs
from write_geojson import write_geojson
from summarize_data import summarize_data
from query_clinicaltrials import query_clinicaltrials


def main():
    """
    analyze data
    """

    print("running main")

    tasks = [5]

    if 0 in tasks: query_gscholar()
    if 1 in tasks: meta_pubs()
    if 2 in tasks: geolocate_pubs()
    if 3 in tasks: write_geojson()

    if 4 in tasks: summarize_data()

    if 5 in tasks: query_clinicaltrials()


    print("completed main")


if __name__ == "__main__":
    main()
