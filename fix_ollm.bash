
cd open_llm_leaderboard
rm lev_app.py
git co model_info_cache.pkl model_size_cache.pkl src/load_from_hub.py
rm lev_app.py
git pull

cd src
perl -pi -e 's/git_pull\(\)/git_pull(lfs=True)/gi;' load_from_hub.py

perl -pi -e 's/git_pull

git_pull(lfs=True)



original_df = get_leaderboard_df(EVAL_RESULTS_PATH, COLS, BENCHMARK_COLS)

print("FINISHED getting original_df")
print(f"len(original_df) = {len(original_df)}")
print()
print(original_df)
print()

# save to file
import time
from os.path import expanduser
time_now = time.strftime("%Y%m%d_%H%M%S")
home_dir = expanduser("~")
mydir = f"{home_dir}/Documents/GitHub/ai"

fname = f"{mydir}/orig_df_{time_now}.csv"
print(f"writing to file {fname}")
original_df.to_csv(fname, index=False)