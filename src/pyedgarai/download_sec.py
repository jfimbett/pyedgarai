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

# Complete the headers, make them look like a browser
HEADERS = {
    "Host": "www.sec.gov",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Cookie": "_ga_300V1CHKH1=GS1.1.1715288471.5.0.1715288471.0.0.0; _ga=GA1.2.1974077178.1714908837; nmstat=ad12f924-2e0f-4785-2f34-985cf2bb5937; _ga_CSLL4ZEK4L=GS1.1.1715288471.6.0.1715288471.0.0.0; _4c_=%7B%22_4c_s_%22%3A%22fZFbT4QwEIX%2FyqbPwLbcWngzazQ%2BqNF4edwALUuzuCVQ6eqG%2F%2B60EKNrIi%2B035xzMp05IdOIA8oJJXFGaJZhzBIP7cXHgPIT6iW3vxHlCJOwiCgufc7L0I9Fyv2sKguf1KwkouYQUCAPHW1WGKYsZlGaRHjyUNUtGSdUKS4gi2QBYQH26wEc%2BtOSEMOx6xV%2Fr%2FRWf3RWZkS5GvgeClyMshJbI7lunN%2FJF9oIuWu0xZg53PX2AicjD1yZc9tCv21ZTIGWvTKDsM4r2YtaHVckTIArGAR6dRbbLZRE3ztdo3U35Ou1MSbYKbVrRVCptzWIBqlt%2F4OooDAuAGY6M39mL9JSvnraPAK%2F%2B0EeNve3C%2BrG5SmtqorWhsK2PHR9sX2%2BuXRPojGmlFAWuBVixiKKpmUPALIkjFjCQpizblHO0hjbb5qj3VrIb3WaJPiveh6Pb9sXh3%2Bs5Nw6TV8%3D%22%7D; ak_bmsc=325E1629AF21BEA2E3AA25FBB970B718~000000000000000000000000000000~YAAQJlfIF+omVsGRAQAAnz+K1RkdzQa9q4NoWHG0QtaviUnfe96C7X/6G1mc2ty2fBvx35CiUMbaXkperV6lkl1AF3/qIpVOXaVj2WSjl6PnqQniqI72fm9MIivLiEYfz1t1zW1vkN5SAYyPnfcyqcsYyjJVwrmJGhwl48jDSGwQiOd2Ep+Lg+d3sRfnZeI6nrvamgAGqCLBJGV5jIX8ExlfKQUEpckphf41NpBZWMctvvD4Hcr7Dw6qeSQbTa7vN6IID2ng5xIlgFc3KQgvvJKaC03FmiGp67m/+W6i7GW8zyyoo9GsvWz6F5JREyv84ObsdkWTEVLRg/ErK056JbrVp9msV8L1yYyfRZ/jRXrXQmYoZ+iuG4WexfsXt5kL2aZz1RM=; bm_mi=B03D935426CED58CDA9B0A1FD1F159B9~YAAQJlfIF/QmVsGRAQAABEGK1Rko8PI8ZuxcEAcoGltXNbYt83gBboG/JhU+cZ8rGFT7JBolLsxNItHfV0GTUwWbxw2opG0Dr9H10DwaDaosWh0vjmJ1ROacr/XL39dqA5pB2t7cJGpQClDRUl9WHF5ZPuusP1ZKWtoAX0HYh4V3cbJmop36MSAQZW2qYW/Qp89hkh2q7FDq2Y5UooIHrlz1yzwBgdT5aDStq2Z45t23I4WquFiiUmFK/wWra2KRSfA+K5DYXILvBFBPH3iXBVeLgNmv6zCCTQcBQF1HLcSe8RqqYys3x6ZN81w95KpmQhk0WpKnl4iSttDygJl77Jwino2WwVoKWlVmh6AhyJuW~1; bm_sv=63A69D4EF6B354AD948C393931DE6D6F~YAAQJlfIF/UmVsGRAQAABEGK1Rlw3JnKUceMDDhXiXZzwoNaQj3tWSW/kw116A2Fvd/WVj796ZZq3vS0Ug5am5yuIWc8K9a+m3ICYGe2/Voa4n7g0+tIUhhLWR+nlBlSUbryAUAzAKvv3weFcMUR/7SPaURAOyz5oIxz/vfRU8KxiYSO9lXQ+iHNjeu5HAJJHtWyBzfII+KlhMTKgC/+VjaYOcdGf/fUJrgeczmcLXWR/KqwYfMQ+KoYoyLG~1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=0, i",
    "TE": "trailers"
}


@dataclass
class Config:
    PATH_TO_DATA = "..\\..\\data" if __name__ == "__main__" else "data"


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




