#!/usr/bin/env python
# coding: utf-8

"""
# --------------------------------------------------------------
# llm_leaderboard.py
# get HuggingFace.co LLM leaderboard data
# using felixz space on HuggingFace
# by Lev Selector, October 2023
# --------------------------------------------------------------
"""

import os, sys, json, time
from gradio_client import Client
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
get_felixz_data(bag)
process_all(bag)
