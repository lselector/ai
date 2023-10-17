
#%%

# --------------------------------------------------------------
# This code comes from 
# https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
# 
# To run it locally I had to:
#  create account and get token, put it into env variable H4_TOKEN
#  clone the repo "open_llm_leaderboard"
#     git lfs install
#     git clone https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
#  cp open_llm_leaderboard/app.py  ./tmp.py
#  code tmp.py
#  take the top portion of app.py until it creates original_df,
#  delete the rest (bottom)
#  modify to save the original_df into csv file
#  save it as lev_app.py and copy it to open_llm_leaderboard/
#
#  then go into "open_llm_leaderboard/src" subdirectory 
#  and make change in load_from_hub.py like this
#      perl -pi -e 's/git_pull\(\)/git_pull(lfs=True)/gi;' load_from_hub.py
# --------------------------------------------------------------

#%%
import os, sys, time
import pandas as pd
from huggingface_hub import HfApi
from os.path import expanduser
#%%

from src.assets.css_html_js import custom_css, get_window_url_params
from src.assets.text_content import (
    CITATION_BUTTON_LABEL,
    CITATION_BUTTON_TEXT,
    EVALUATION_QUEUE_TEXT,
    INTRODUCTION_TEXT,
    LLM_BENCHMARKS_TEXT,
    TITLE,
)
from src.display_models.get_model_metadata import DO_NOT_SUBMIT_MODELS, ModelType
from src.display_models.modelcard_filter import check_model_card
from src.display_models.utils import (
    AutoEvalColumn,
    EvalQueueColumn,
    fields,
    styled_error,
    styled_message,
    styled_warning,
)
from src.load_from_hub import get_evaluation_queue_df, get_leaderboard_df, is_model_on_hub, load_all_info_from_hub
from src.rate_limiting import user_submission_permission
#%%

pd.set_option("display.precision", 1)

# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)

QUEUE_REPO = "open-llm-leaderboard/requests"
RESULTS_REPO = "open-llm-leaderboard/results"

PRIVATE_QUEUE_REPO = "open-llm-leaderboard/private-requests"
PRIVATE_RESULTS_REPO = "open-llm-leaderboard/private-results"

IS_PUBLIC = bool(os.environ.get("IS_PUBLIC", True))

EVAL_REQUESTS_PATH = "eval-queue"
EVAL_RESULTS_PATH = "eval-results"

EVAL_REQUESTS_PATH_PRIVATE = "eval-queue-private"
EVAL_RESULTS_PATH_PRIVATE = "eval-results-private"

api = HfApi(token=H4_TOKEN)
#%%


def restart_space():
    api.restart_space(repo_id="HuggingFaceH4/open_llm_leaderboard", token=H4_TOKEN)

#%%

# Rate limit variables
RATE_LIMIT_PERIOD = 7
RATE_LIMIT_QUOTA = 5

# Column selection
COLS = [c.name for c in fields(AutoEvalColumn) if not c.hidden]
TYPES = [c.type for c in fields(AutoEvalColumn) if not c.hidden]
COLS_LITE = [c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.hidden]
TYPES_LITE = [c.type for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.hidden]

if not IS_PUBLIC:
    COLS.insert(2, AutoEvalColumn.precision.name)
    TYPES.insert(2, AutoEvalColumn.precision.type)

EVAL_COLS = [c.name for c in fields(EvalQueueColumn)]
EVAL_TYPES = [c.type for c in fields(EvalQueueColumn)]

BENCHMARK_COLS = [
    c.name
    for c in [
        AutoEvalColumn.arc,
        AutoEvalColumn.hellaswag,
        AutoEvalColumn.mmlu,
        AutoEvalColumn.truthfulqa,
    ]
]
#%%

## LOAD INFO FROM HUB
eval_queue, requested_models, eval_results, users_to_submission_dates = load_all_info_from_hub(
    QUEUE_REPO, RESULTS_REPO, EVAL_REQUESTS_PATH, EVAL_RESULTS_PATH
)
#%%
if not IS_PUBLIC:
    (eval_queue_private, requested_models_private, eval_results_private, _) = load_all_info_from_hub(
        PRIVATE_QUEUE_REPO,
        PRIVATE_RESULTS_REPO,
        EVAL_REQUESTS_PATH_PRIVATE,
        EVAL_RESULTS_PATH_PRIVATE,
    )
else:
    eval_queue_private, eval_results_private = None, None
#%%

original_df = get_leaderboard_df(eval_results, eval_results_private, COLS, BENCHMARK_COLS)

#%%
print("FINISHED getting original_df")
print(f"len(original_df) = {len(original_df)}")
print()
print(original_df)
print()

# save to file
import time
time_now = time.strftime("%Y%m%d_%H%M%S")
home_dir = expanduser("~")
mydir = f"{home_dir}/Documents/GitHub/ai"

fname = f"{mydir}/orig_df_{time_now}.csv"
print(f"writing to file {fname}")
original_df.to_csv(fname, index=False)

