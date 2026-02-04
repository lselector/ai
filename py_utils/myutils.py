import os, sys, pickle, re, json, time
import datetime as dt
import unidecode as ud
from mybag        import *
from util_jupyter import *

# --------------------------------------------------------------
def date_valid(date_str=None, fmt='%Y-%m-%d'):
    """ 
    # checks if date_str is a valid date
    # by default expects date as YYYY-MM-DD
    # Examples of usage:
    #   date_valid('2015-03-24')
    #   date_valid('03/24/2015','%m/%d/%Y')
    """
    try:
        dt.datetime.strptime(date_str, fmt)
        return True
    except:
        return False

# --------------------------------------------------------------
def days_start_to_end(bag):
    """
    # returns number of days for which we run report.
    # if it is daily report - returns 1
    # for monthly - returns number of days in this month
    """
    dt1 = dt.datetime.strptime(bag.date1, '%Y-%m-%d')
    dt2 = dt.datetime.strptime(bag.date2, '%Y-%m-%d')
    return (dt2 - dt1).days

# --------------------------------------------------------------
def get_date_shifted_by_days(start_date, num_days):
    """
    # accepts and returns date as string YYYY-MM-DD 
    # also accepts shift (in days, int)
    """
    return (dt.datetime.strptime(start_date,'%Y-%m-%d') + dt.timedelta(num_days)).strftime('%Y-%m-%d')

# --------------------------------------------------------------
def today_yyyymmdd():
    """ returns string for today in format YYYYMMDD """
    yyyy,mm,dd = str(dt.date.today()).split('-')
    return "%s%s%s" % (yyyy,mm,dd)

# --------------------------------------------------------------
def today_yyyy_mm_dd():
    """ returns string for today in format YYYY-MM-DD """
    yyyy,mm,dd = str(dt.date.today()).split('-')
    return "%s-%s-%s" % (yyyy,mm,dd)

# --------------------------------------------------------------
def now_str():
    """ returns current date-time as YYYY-MM-DD HH:MM:SS """
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------------------------------------------------------------
def sec_to_hms(secs):
    """ converts seconds into string in format "HH:MM:SS" """
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    h_str = "%d"   % int(h)
    m_str = "%02d" % int(m)
    s_str = "%02.2f" % round(s,2)
    s_str = re.sub(r'\.00$','',s_str)
    return ':'.join([h_str,m_str,s_str])

# --------------------------------------------------------------
def elapsed_time(bag, t1=None):
    """
    # returns time elapsed from beginning of the script in seconds
    # optionally accepts another starting point (in epoch seconds)
    """
    if t1 == None:
        t1 = bag.script_start_time
    t2 = time.time()
    return round(t2-t1,2)

# --------------------------------------------------------------
def elapsed_time_hms(bag, t1=None):
    """
    # returns time elapsed from beginning of the script as string:
    #   HH:MM:SS , or HH:MM:SS.DD
    # optionally accepts another starting point (in epoch seconds)
    """
    return sec_to_hms(elapsed_time(bag, t1))

# --------------------------------------------------------------
def print_elapsed_time(bag, t1=None):
    """
    # prints current date/time, and time elapsed from beginning of the script
    # optionally accepts another starting point (in epoch seconds)
    # depends on bag.script_start_time and bag.script_cmd
    """
    time_now   = now_str()
    if not t1:
        t1 = bag.script_start_time
    elapsed    = elapsed_time_hms(bag, t1)
    script_cmd = bag.script_cmd
    print(f"{time_now} FINISHED ( {script_cmd} ), elapsed time was {elapsed}")

# --------------------------------------------------------------
def write_bag_to_pk(bag,fname):
    """ writing bag to pickle file """
    print(f"writing bag to pickle file {fname}")
    with open(fname, 'wb') as fh:
        pickle.dump(bag, fh, protocol=pickle.HIGHEST_PROTOCOL)

# --------------------------------------------------------------
def read_pk_to_bag(fname):
    """ reading pickle file into the bag variable """
    print(f"reading file {fname} into the bag variable")
    with open(fname, 'rb') as fh:
        bag = pickle.load(fh)
    return bag

# --------------------------------------------------------------
def replace_multiple_underscores(fname):
    """ replace multiple underscores to single underscore """
    ss = re.sub(r'_+'    , '_', fname)
    return ss

# --------------------------------------------------------------
def title_to_alphanum(title):
    """ converts title into alphanumeric string with underscores """
    ascii_title = ud.unidecode(title)
    alphanum = ''.join(c if c.isalnum() else '_' for c in ascii_title)
    alphanum = replace_multiple_underscores(alphanum)
    return alphanum

# ---------------------------------------------------------------
def myrun(cmd):
    """ simple function to run shell command and return a string """
    try:
        txt = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        txt = e.output
    txt = txt.decode().strip()
    return txt

# --------------------------------------------------------------
def convert_to_json(bag):
    """ writes scraped data into JSON file """
    mydict = { 
        "title"    : bag.title,
        "text"     : bag.content,
        "date"     : bag.date,
        "date_run" : bag.date_run,
        "link"     : bag.url
    }

    os.makedirs(bag.directory_path, exist_ok=True)
    with open(bag.directory_path + bag.file_name + ".json", "w", encoding="utf-8") as fh:
        json.dump(mydict, fh, indent=4) 

