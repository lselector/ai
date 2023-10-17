#!/usr/bin/env python
# coding: utf-8

"""
# --------------------------------------------------------------
# llm_leaderboard_2.py
# get HuggingFace.co LLM leaderboard data
# by Lev Selector, October 2023
# first run
#     cd open_llm_leaderboard
#     python lev_app.py
# to get the data into file like this:
#     orig_df_20231013_084845.csv
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
from process_all import *

bag = MyBunch()
bag.error_flag = 0
bag.home_dir = expanduser("~")
bag.mydir = f"{bag.home_dir}/Documents/GitHub/ai"
get_data_from_orig_df_file(bag)
process_all(bag)
