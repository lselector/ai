#!/usr/bin/env python
# coding: utf-8

"""
# --------------------------------------------------------------
# llm_leaderboard_2.py
# get HuggingFace.co LLM leaderboard data
# by Lev Selector, Oct-Nov 2023
# first get a fresh clone of the space repo
# and modify the app.py as described here:
#    HOW_TO_run_app_py_locally.txt
# Then
#     cd open_llm_leaderboard
#     python app.py
# to get the data into file like this:
#     orig_df_20231110_084845.csv
#
# Then run this script to read the latest file
# and create Excel files for review
# --------------------------------------------------------------
"""

import os, sys, json, time, glob
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from os.path import expanduser
from mybag import *
from process_lib import *

bag = MyBunch()
bag.error_flag = 0
bag.home_dir = expanduser("~")
bag.mydir = f"{bag.home_dir}/Documents/GitHub/ai"
get_data_from_orig_df_file(bag)
process_all(bag)
