#%%
import requests 
import zipfile
import os
from tqdm import tqdm
from dataclasses import dataclass
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import timedelta
import time

# SEC policy: include a descriptive UA with contact
HEADERS = {
    "User-Agent": "pyedgarai (github.com/jfimbett/pyedgarai)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}

@dataclass
class Config:
    PATH_TO_DATA = os.getenv("PYEDGARAI_DATA_DIR", ("..\\..\\data" if __name__ == "__main__" else "data"))


def download_zip_sec(url, save_path, chunk_size):
    try:
        r = requests.get(url, stream=True, headers=HEADERS)
        
        # check respomnse 
        if r.status_code != 200:
            raise Exception(f"Error {r.status_code} in request {url}")
        
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)

        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(save_path.replace(".zip",""))

        os.remove(save_path)
        #print(f"Financial Data from {url} downloaded...")
    except Exception as e:
        print(f"Error downloading {url} : {e}")

def download_url_sec(urls, chunk_size=128, config=Config()):
    """download_url_sec downloads the sec financial data from the sec website

    Args:
        urls (list str): urls of zip files to download
        chunk_size (int, optional): Chunk size to make the download more smooth. Defaults to 128.
    """

    # Check that folder sec exists, otherwise create it
    path_to_save = os.path.join(config.PATH_TO_DATA, 'sec')
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    for url in tqdm(urls):
        # the name of the zip file is at the end of the url
        name = url.split('/')[-1]
        save_path=os.path.join(path_to_save, name)
        download_zip_sec(url, save_path, chunk_size)


def update_all_data():
    """update_all_data downloads the latest data from the sec website and processes it
    """
    
    url = "https://www.sec.gov/dera/data/financial-statement-data-sets.html"
    r = requests.get(url, headers=HEADERS)
    
    # check response 
    if r.status_code != 200:
        raise Exception(f"Error {r.status_code} in request {url}")
    
    soup = bs(r.content, 'html.parser')

    # get the table in soup
    table = soup.find('table')
    # get the rows in the table
    rows = table.find_all('tr')
    # print the rows
    urls = []
    for row in rows[1:]:
        d = row.find_all('td')[0].find_all('a')[0]
        #append d['href] to the base url
        urls.append(f"https://www.sec.gov{d['href']}")

    download_url_sec(urls)

def get_folder_size_in_gb(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            # Ensure the file exists to avoid errors
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    # Convert bytes to gigabytes
    size_in_gb = total_size / (1024 ** 3)
    return size_in_gb

def display_size():
    folder_path = Config().PATH_TO_DATA
    size_gb = get_folder_size_in_gb(folder_path)
    return size_gb

def prepare_data_quarter_year(year, quarter, config=Config()):
    main_path=os.path.join(config.PATH_TO_DATA, 'sec', f"{year}q{quarter}")
    if not os.path.exists(main_path):
        return
    num = pd.read_csv(os.path.join(main_path, "num.txt"), sep="\t", low_memory=False)
    sub = pd.read_csv(os.path.join(main_path, "sub.txt"), sep="\t", low_memory=False)
    tag = pd.read_csv(os.path.join(main_path, "tag.txt"), sep="\t", low_memory=False)

    # keep only if us-gaap appears or dei
    num = num[num.version.str.contains('us-gaap') | num.version.str.contains('dei')]
    if len(num)==0:
        return
    
    # now we merge (inner join e.g. keep if _merge==3 in Stata) with sub
    df = pd.merge(num,sub,on='adsh')

    df.accepted = df.accepted.apply(lambda x : x[:-11])

    df['t_day']=pd.to_datetime(df.accepted, format='%Y-%m-%d')

    # Now, info is only available to the public until next day of being accepted
    df['t_day']=df['t_day']+timedelta(days=1)

    # We keep the one referring to the latest date of report, 
    df = df.sort_values(['cik','tag', 't_day', 'ddate'])
    df = df.groupby(['cik', 'tag', 't_day']).tail(1)

    # save in folder, and delete .txt files
    # save as parquet
    df.to_parquet(os.path.join(main_path, "data.parquet"))
    os.remove(os.path.join(main_path, "num.txt"))
    os.remove(os.path.join(main_path, "sub.txt"))
    os.remove(os.path.join(main_path, "tag.txt"))
    os.remove(os.path.join(main_path, "pre.txt"))
    os.remove(os.path.join(main_path, "readme.htm"))

def prepare_all_data(config=Config()):
    # automatically get the current year 
    max_year = pd.Timestamp.now().year
    max_month = pd.Timestamp.now().month
    current_quarter = (max_month-1)//3+1

    iterations = [(year, quarter) for year in range(2009, max_year+1) for quarter in range(1, 5) if not ( quarter>=current_quarter and year==pd.Timestamp.now().year)]
    pbar = tqdm(iterations)
    for year, quarter in pbar:
        pbar.set_description(f"Processing {year}q{quarter}")
        pbar.refresh()
        try:
            prepare_data_quarter_year(year, quarter, config)
        except Exception as e:
            print(f"Error in {year}q{quarter}: {e}")

def pivot_variables(df, accounts = [], ciks=[]):
    # confirm variables exist (value and qtrs) in df
    if 'value' not in df.columns or 'qtrs' not in df.columns:
        return

    # keep only accounts in accounts
    if len(accounts)>0:
        df = df[df.tag.isin(accounts)]

    # if ciks not empty, keep only ciks in ciks
    if len(ciks)>0:
        df = df[df.cik.isin(ciks)]

    df= df.rename(columns={'value': 'v'})
    df= df.drop(['qtrs'], axis=1)

    # drop ddate accepted
    df=df.drop(['accepted'], axis=1)


    df=df.pivot_table(index=["cik", "t_day", 'ddate', 'sic'], 
                        columns='tag', 
                        values='v').reset_index()
    
    return df

import time

def timing(unit="ms"):
    def decorator(f):
        def wrap(*args, **kwargs):
            time1 = time.time()
            ret = f(*args, **kwargs)
            time2 = time.time()
            
            elapsed_time = time2 - time1
            if unit == "ms":
                print(f'Function {f.__name__} took {elapsed_time * 1000.0:.1f} ms')
            elif unit == "s":
                print(f'Function {f.__name__} took {elapsed_time:.1f} s')
            elif unit == "m":
                print(f'Function {f.__name__} took {elapsed_time / 60.0:.1f} m')
            else:
                raise ValueError(f"Unsupported unit: {unit}")
            
            return ret
        return wrap
    return decorator


@timing("m")
def download_and_prepare_data():
    update_all_data()
    path = Config().PATH_TO_DATA
    size_gb = get_folder_size_in_gb(path)

    prepare_all_data()

    size_gb_a = get_folder_size_in_gb(path)

    print(f"Size of data folder before: {size_gb:.2f} GB")
    print(f"Size of data folder after: {size_gb_a:.2f} GB")
    # how much space was saved
    print(f"Space saved: {size_gb-size_gb_a:.2f} GB")

# alternative way to get data where we pivot every df instead of just one at the end 
@timing("m")
def get_data(ciks, accounts, config = Config()):
    # append all the data
    base_path = os.path.join(config.PATH_TO_DATA, 'sec')
    to_append = []
    # loop through all folders inside base_path
    for path in os.listdir(base_path):
        file_path = os.path.join(base_path, path, "data.parquet")
        if not os.path.exists(file_path):
            continue
        df = pd.read_parquet(file_path)
        # pivot the data
        df = pivot_variables(df, accounts=accounts, ciks = ciks)
        to_append.append(df)
    
    # concat all the data
    df = pd.concat(to_append)

    return df




