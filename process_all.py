#!/usr/bin/env python
# coding: utf-8

"""
# --------------------------------------------------------------
# process_all.py
# functions to be called from llm_leaderboard*.py
# --------------------------------------------------------------
"""

import os, sys, json, time, glob
from gradio_client import Client
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from os.path import expanduser
from mybag import *


# --------------------------------------------------------------
def get_data_from_orig_df_file(bag):
    files = sorted(glob.glob(f"{bag.mydir}/orig_df_20*.csv"), reverse=True)
    if len(files) >= 0:
        fname_in = files[0]
        print(f"reading file {fname_in}")
        bag.df = pd.read_csv(fname_in)
    else:
        print("ERROR, didn't find any input files like orig_df_YYYYMMDD_HHMMSS.csv")
        print("Exiting ...")
        sys.exit()

    bag.mylen = len(bag.df)
    print(f"len(bag.df) = {bag.mylen}")

# --------------------------------------------------------------
def get_felixz_data(bag):
    """ get data using gradio client from felixz space """
    client = Client("https://felixz-open-llm-leaderboard.hf.space/")
    json_data = client.predict("","", api_name='/predict')
    with open(json_data, 'r') as file:
        file_data = file.read()
    # Load the JSON data
    data = json.loads(file_data)
    headers = data['headers'] # list of table headers
    data = data['data'] 
    df = pd.DataFrame(data=data, columns=headers)
    bag.mylen = len(df)
    print(f"len(df) = {len(df)}")
    bag.df = df

# --------------------------------------------------------------
def select_columns(bag):
    """ select and rename columns """
    mycols = ['model_name_for_query','Average ⬆️','ARC','HellaSwag','MMLU',
                  'TruthfulQA','Type','Precision', '#Params (B)', 'Model']
    bag.df = bag.df[mycols].copy()

    # rename columns
    bag.mycols = ['Model','Aver','ARC','HellaSwag','MMLU','TruthfulQA', 
            'Type','Precision', 'Nparam','model_link']
    bag.df.columns = bag.mycols

# --------------------------------------------------------------
def simplify_url(bag):
    """ simplify url in model_link column """
    def myurl(x):
        soup = BeautifulSoup(x, 'html.parser')
        link = soup.find_all('a')
        if len(link) <= 0:
            return ""
        link = link[0] 
        return link.get('href')

    bag.df['model_link'] = bag.df['model_link'].map(lambda x: myurl(x))

# --------------------------------------------------------------
def add_gpt(bag):
    """ 
    # add gpt4 and gpt3.5 
    # https://platform.openai.com/docs/models
    # https://arxiv.org/abs/2303.08774
    """
    mylist = [
        ['GPT-4', 84.3, 96.3, 95.3, 86.4, 59, 'Unknown', 'torch.float16', 1800.00, 'GPT-4'],
        ['GPT-3.5', 71.9, 85.2, 85.5, 70, 47, 'Unknown', 'torch.float16', 175.00, 'GPT-3.5']
    ]
    df2 = pd.DataFrame(mylist, columns = bag.mycols)
    bag.df = pd.concat([bag.df, df2], ignore_index = True)

# --------------------------------------------------------------
def simplify_precision(bag):
    """ simplify Precision column """
    def myprecision(x):
        x = str(x)
        if "torch" in x:
            x = x.replace("torch.float","")
            x = x.replace("torch.bfloat","")
            x = x + "bit"
        return x
        
    bag.df['Precision'] = bag.df['Precision'].map(lambda x: myprecision(x))

# --------------------------------------------------------------
def sort_and_add_index(bag):
    """ sort by average score and add index column """
    bag.df = bag.df.sort_values(by=['Aver'], ascending=False)
    print(bag.df)
    bag.mylen = len(bag.df)
    bag.df.insert(0, "Rank", list(range(bag.mylen)))
    bag.df.index = range(bag.mylen)

# --------------------------------------------------------------
def df_to_csv_xlsx(bag):
    """ save df to csv and excel """
    bag.time_now = time.strftime("%Y%m%d_%H%M%S")
    bag.fname = f"llm_leaderboard_{bag.time_now}"
    bag.fname = bag.mydir + "/" + bag.fname
    fname_csv = bag.fname + ".csv"
    print(f"writing to file {fname_csv}")
    bag.df.to_csv(fname_csv, index=False)
    fname_xls = bag.fname + ".xlsx"
    print(f"writing to file {fname_xls}")
    bag.df.to_excel(fname_xls, index=False)

# --------------------------------------------------------------
# create mask to select only interesting rows 

def mask_make1(bag):
    """ start making mask for interesting rows """
    # first 3 rows and very last row
    bag.mask = ( bag.df['Rank'].isin([0,1,2,bag.mylen-1])) | bag.df['Model'].isin(['GPT-4','GPT-3.5'])

    # add top 8bit model
    myrank = bag.df.loc[bag.df['Precision'] == '8bit'].iloc[0]["Rank"]
    bag.mask = bag.mask | ( bag.df['Rank'] == myrank )

    # add top 4bit model
    myrank = bag.df.loc[bag.df['Precision'] == '4bit'].iloc[0]["Rank"]
    bag.mask = bag.mask | ( bag.df['Rank'] == myrank )
    bag.m0 = []

# --------------------------------------------------------------
def add_to_mask(bag):
    """ 
    # convenience function to add rows to bag.mask 
    # add only top model with this mask
    """
    dft = bag.df.loc[ bag.m0 ]
    if len(dft) > 0:
        myrank = bag.df.loc[ bag.m0 ].iloc[0]["Rank"]
        bag.mask = bag.mask | ( bag.df['Rank'] == myrank )

# --------------------------------------------------------------
def mask_make2(bag):
    """ add original LLaMa2 and Mistral"""
    for ss in ['tiiuae/falcon-180B',
            'meta-llama/Llama-2-70b-chat-hf',
            'mistral',
            'mistralai/Mistral-7B-v0.1',
            'Open-Orca/Mistral-7B-OpenOrca'
            ]:
        bag.m0 = bag.df['Model'].str.contains(ss, na=False, case=False)
        add_to_mask(bag) # add only top model with this string

# --------------------------------------------------------------
def mask_make3(bag):
    """ add more small models """
    # top 7b, 11b, 13b models
    for ss in ["-13b", "11b", "-7b"]:
        bag.m0 = bag.df['Model'].str.contains(ss, na=False, case=False) 
        add_to_mask(bag)

    # top 4bit 7b, 11b, 13b models
    for ss in ["-13b", "11b", "-7b"]:
        bag.m0 = bag.df['Model'].str.contains(ss, na=False, case=False) 
        bag.m0 = bag.m0 & (bag.df['Precision'] == '4bit')
        add_to_mask(bag)

    # top Mistral + OpenOrca
    bag.m0 = bag.df['Model'].str.contains('mistral', na=False, case=False) \
           & bag.df['Model'].str.contains('OpenOrca', na=False, case=False)
    add_to_mask(bag)

    # top Mistral + 4bit
    bag.m0 = bag.df['Model'].str.contains('mistral', na=False, case=False) \
           & bag.df['Precision'].str.contains('4bit', na=False, case=False)
    add_to_mask(bag)

# --------------------------------------------------------------
def mask_apply(bag):
    """ use the mask to get only several interesting rows """
    bag.df2 = bag.df[bag.mask].copy()
    bag.df2 = bag.df2.drop_duplicates()
    bag.df2 = bag.df2.sort_values(by=['Rank'])

# --------------------------------------------------------------
def df2_round_params(bag):
    """ round up Nparam in bag.df2 """

    def round_nparam(x):
        """ round up Nparam """
        if (x > 6.5) and (x<7.5):
            return 7
        if (x > 10.5) and (x<11.5):
            return 11
        if (x > 12.5) and (x<13.5):
            return 13
        if (x > 25) and (x<35):
            return 30
        if (x > 65) and (x<75):
            return 70
        return x

    bag.df2['Nparam'] = bag.df2['Nparam'].map(lambda x: round_nparam(x))

# --------------------------------------------------------------
def df2_to_xlsx(bag):
    """ write selected models into small Excel file """
    mycols = ["Rank", "Model", "Aver", "Precision", "Nparam"]
    bag.df2 = bag.df2[mycols].copy()
    print(bag.df2)

    fname_selected = bag.fname + "_selected.xlsx"
    print(f"writing to file {fname_selected}")
    bag.df2.to_excel(fname_selected, index=False)

# ---------------------------------------------------------------
def process_all(bag):
    select_columns(bag)
    simplify_url(bag)
    add_gpt(bag)
    simplify_precision(bag)
    sort_and_add_index(bag)
    df_to_csv_xlsx(bag)
    mask_make1(bag)
    add_to_mask(bag)
    mask_make2(bag)
    mask_make3(bag)
    mask_apply(bag)
    df2_round_params(bag)
    df2_to_xlsx(bag)

# ---------------------------------------------------------------
