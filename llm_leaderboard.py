#!/usr/bin/env python
# coding: utf-8

"""
# --------------------------------------------------------------
# llm_leaderboard.py
# get HuggingFace.co LLM leaderboard data
# by Lev Selector, October 2023
# --------------------------------------------------------------
"""

import os, sys, json, time
from gradio_client import Client
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

client = Client("https://felixz-open-llm-leaderboard.hf.space/")

json_data = client.predict("","", api_name='/predict')

with open(json_data, 'r') as file:
    file_data = file.read()

# --------------------------------------------------------------
# Load the JSON data
data = json.loads(file_data)
headers = data['headers'] # list of table headers

# ['T','Model','Average ⬆️','ARC','HellaSwag','MMLU','TruthfulQA',
#  'Type','Precision','Hub License','#Params (B)','Hub ❤️',
#  'Available on the hub','Model sha','model_name_for_query']

data = data['data'] 
# list of more than thousand elements
# each element is a list like this
# 
# [
# '🔶', 
# '<a target="_blank" href="https://huggingface.co/AIDC-ai-business/Marcoroni-70B-v1" ...">📑</a>',
# 74.06,
# 73.55,
# 87.62,
# 70.67,
# 64.41,
# 'fine-tuned',
# 'torch.bfloat16',
# 'cc-by-nc-4.0',
# 68.72,
# 14,
# True,
# '55a30d29db194832c0b5de1392a6598a63582144',
# 'AIDC-ai-business/Marcoroni-70B-v1'] 

df = pd.DataFrame(data=data, columns=headers)

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
    ['GPT-3.5', 71.9, 85.2, 85.5, 70, 47, 'Unknown', 'torch.float16', 175.00, 'GPT-3.5'],
    ['Open-Orca/Mistral-7B-OpenOrca', 65.84, 64.08, 83.99, 62.24, 53.05, 'fine-tuned', 'torch.float16', 
     7.3, 'https://huggingface.co/Open-Orca/Mistral-7B-OpenOrca']
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
mydir = os. getcwd()
fname = mydir + "/" + fname
# fname_csv = fname + ".csv"
# print(f"writing to file {fname_csv}")
# df.to_csv(fname_csv, index=False)
fname_xls = fname + ".xlsx"
print(f"writing to file {fname_xls}")
df.to_excel(fname_xls, index=False)

# --------------------------------------------------------------
# Select interesting rows only 
mask = ( df['Rank'].isin([0,1,2,mylen-1])) | df['Model'].isin(['GPT-4','GPT-3.5'])

myrank = df.loc[df['Precision'] == '8bit'].iloc[0]["Rank"]
mask = mask | ( df['Rank'] == myrank )

myrank = df.loc[df['Precision'] == '4bit'].iloc[0]["Rank"]
mask = mask | ( df['Rank'] == myrank )

for ss in ['tiiuae/falcon-180B',
           'meta-llama/Llama-2-70b-chat-hf',
           'Open-Orca/Mistral-7B-OpenOrca',
           'mistralai/Mistral-7B-v0.1'
          ]:
    m0 = df['Model'].str.contains(ss)
    dft = df.loc[ m0 ]
    if len(dft) > 0:
        myrank = df.loc[ m0 ].iloc[0]["Rank"]
        mask = mask | ( df['Rank'] == myrank )

# top -13B model
for ss in ["-13B", "-7B"]:
    sss = ss.lower()
    m0 = df['Model'].str.contains(ss) | df['Model'].str.contains(ss.lower())
    m0 = m0 & (df['Precision'] == '4bit')
    dft = df.loc[m0]
    if len(dft) > 0:
        myrank = df.loc[m0].iloc[0]["Rank"]
        mask = mask | ( df['Rank'] == myrank )

df2 = df[mask].copy()
df2 = df2.drop_duplicates()
df2 = df2.sort_values(by=['Rank'])

# round up Nparam

def round_nparam(x):
    if (x > 6.5) and (x<7.5):
        return 7
    if (x > 12.5) and (x<13.5):
        return 13
    if (x > 25) and (x<35):
        return 30
    if (x > 65) and (x<75):
        return 70
    return x

df2['Nparam'] = df2['Nparam'].map(lambda x: round_nparam(x))

mycols = ["Rank", "Model", "Aver", "Precision", "Nparam"]
df2 = df2[mycols].copy()
print(df2)

fname_selected = fname + "_selected.xlsx"

print(f"writing to file {fname_selected}")
df2.to_excel(fname_selected, index=False)

