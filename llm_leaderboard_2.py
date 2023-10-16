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
#%%
import os, sys, json, time, glob
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from os.path import expanduser

home_dir = expanduser("~")
mydir = f"{home_dir}/Documents/GitHub/ai"

#%%
files = sorted(glob.glob(f"{mydir}/orig_df_20*.csv"), reverse=True)
if len(files) >= 0:
    fname_in = files[0]
    print(f"reading file {fname_in}")
    df = pd.read_csv(fname_in)
else:
    print("ERROR, didn't find any input files like orig_df_YYYYMMDD_HHMMSS.csv")
    print("Exiting ...")
    sys.exit()
#%%

mylen = len(df)
print(f"len(df) = {len(df)}")

# --------------------------------------------------------------
# select some columns
mycols = ['model_name_for_query','Average ⬆️','ARC','HellaSwag','MMLU','TruthfulQA', 
          'Type','Precision', '#Params (B)', 'Model']
df = df[mycols].copy()

# rename columns
mycols = ['Model','Aver','ARC','HellaSwag','MMLU','TruthfulQA', 
          'Type','Precision', 'Nparam','model_link']
df.columns = mycols

# --------------------------------------------------------------
# simplify URL
def myurl(x):
    soup = BeautifulSoup(x, 'html.parser')
    link = soup.find_all('a')
    if len(link) <= 0:
        return ""
    link = link[0] 
    return link.get('href')

df['model_link'] = df['model_link'].map(lambda x: myurl(x))

# --------------------------------------------------------------
# add gpt4 and gpt3.5
# https://platform.openai.com/docs/models
# https://arxiv.org/abs/2303.08774

mylist = [
    ['GPT-4', 84.3, 96.3, 95.3, 86.4, 59, 'Unknown', 'torch.float16', 1800.00, 'GPT-4'],
    ['GPT-3.5', 71.9, 85.2, 85.5, 70, 47, 'Unknown', 'torch.float16', 175.00, 'GPT-3.5']
]

df2 = pd.DataFrame(mylist, columns = mycols)
df = pd.concat([df, df2], ignore_index = True)

def myprecision(x):
    x = str(x)
    if "torch" in x:
        x = x.replace("torch.float","")
        x = x.replace("torch.bfloat","")
        x = x + "bit"
    return x
    
df['Precision'] = df['Precision'].map(lambda x: myprecision(x))

# --------------------------------------------------------------
# sort by average score
df = df.sort_values(by=['Aver'], ascending=False)
print(df)

# --------------------------------------------------------------
# add index column
mylen = len(df)
df.insert(0, "Rank", list(range(mylen)))

# --------------------------------------------------------------
# save to file
time_now = time.strftime("%Y%m%d_%H%M%S")
fname = f"llm_leaderboard_{time_now}"
fname = mydir + "/" + fname
fname_csv = fname + ".csv"
print(f"writing to file {fname_csv}")
df.to_csv(fname_csv, index=False)
fname_xls = fname + ".xlsx"
print(f"writing to file {fname_xls}")
df.to_excel(fname_xls, index=False)

# --------------------------------------------------------------
# create mask to select only interesting rows 

# first 3 rows and very last row
mask = ( df['Rank'].isin([0,1,2,mylen-1])) | df['Model'].isin(['GPT-4','GPT-3.5'])

# add top 8bit model
myrank = df.loc[df['Precision'] == '8bit'].iloc[0]["Rank"]
mask = mask | ( df['Rank'] == myrank )

# add top 4bit model
myrank = df.loc[df['Precision'] == '4bit'].iloc[0]["Rank"]
mask = mask | ( df['Rank'] == myrank )

def add_to_mask():
    global df, mask, m0
    dft = df.loc[ m0 ]
    if len(dft) > 0:
        myrank = df.loc[ m0 ].iloc[0]["Rank"]
        mask = mask | ( df['Rank'] == myrank )

for ss in ['tiiuae/falcon-180B',
           'meta-llama/Llama-2-70b-chat-hf',
           'mistral',
           'mistralai/Mistral-7B-v0.1',
           'Open-Orca/Mistral-7B-OpenOrca'
          ]:
    m0 = df['Model'].str.contains(ss, na=False, case=False)
    add_to_mask()

# top 7b, 11b, 13b models
for ss in ["-13b", "11b", "-7b"]:
    m0 = df['Model'].str.contains(ss, na=False, case=False) 
    add_to_mask()

# top 4bit 7b, 11b, 13b models
for ss in ["-13b", "11b", "-7b"]:
    m0 = df['Model'].str.contains(ss, na=False, case=False) 
    m0 = m0 & (df['Precision'] == '4bit')
    add_to_mask()

# top Mistral + OpenOrca
m0 = df['Model'].str.contains('mistral', na=False, case=False) \
   & df['Model'].str.contains('OpenOrca', na=False, case=False)
add_to_mask()

# top Mistral + 4bit
m0 = df['Model'].str.contains('mistral', na=False, case=False) \
   & df['Precision'].str.contains('4bit', na=False, case=False)
add_to_mask()

# --------------------------------------------------------------
# use the mask to get only several interesting rows

df2 = df[mask].copy()
df2 = df2.drop_duplicates()
df2 = df2.sort_values(by=['Rank'])

# --------------------------------------------------------------
# round up Nparam

def round_nparam(x):
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

df2['Nparam'] = df2['Nparam'].map(lambda x: round_nparam(x))

# --------------------------------------------------------------
mycols = ["Rank", "Model", "Aver", "Precision", "Nparam"]
df2 = df2[mycols].copy()
print(df2)

fname_selected = fname + "_selected.xlsx"

print(f"writing to file {fname_selected}")
df2.to_excel(fname_selected, index=False)


# %%
