#%%
import requests
import re
from bs4 import BeautifulSoup as bs
from markdownify import markdownify as md
from tqdm import tqdm
import json
import outlines

# Load our model
model = outlines.models.transformers("microsoft/Phi-3.5-mini-instruct")

# Classification function
yesno = outlines.generate.choice(model, ['Yes', 'Maybe', 'No'])


class Data:
    pass

# Updated headers to match those observed in the browser
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en;q=0.5",
    "Connection": "keep-alive",
    "Host": "data.sec.gov",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"  # Replace with an actual user-agent string if needed
}

HEADERS_HTM =  {
    "Host": "www.sec.gov",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Cookie": "_ga_300V1CHKH1=GS1.1.1715288471.5.0.1715288471.0.0.0; _ga=GA1.2.1974077178.1714908837; nmstat=ad12f924-2e0f-4785-2f34-985cf2bb5937; _ga_CSLL4ZEK4L=GS1.1.1715288471.6.0.1715288471.0.0.0; _4c_=%7B%22_4c_s_%22%3A%22fZFbT4QwEIX%2FyqbPwLbcWngzazQ%2BqNF4edwALUuzuCVQ6eqG%2F%2B60EKNrIi%2B035xzMp05IdOIA8oJJXFGaJZhzBIP7cXHgPIT6iW3vxHlCJOwiCgufc7L0I9Fyv2sKguf1KwkouYQUCAPHW1WGKYsZlGaRHjyUNUtGSdUKS4gi2QBYQH26wEc%2BtOSEMOx6xV%2Fr%2FRWf3RWZkS5GvgeClyMshJbI7lunN%2FJF9oIuWu0xZg53PX2AicjD1yZc9tCv21ZTIGWvTKDsM4r2YtaHVckTIArGAR6dRbbLZRE3ztdo3U35Ou1MSbYKbVrRVCptzWIBqlt%2F4OooDAuAGY6M39mL9JSvnraPAK%2F%2B0EeNve3C%2BrG5SmtqorWhsK2PHR9sX2%2BuXRPojGmlFAWuBVixiKKpmUPALIkjFjCQpizblHO0hjbb5qj3VrIb3WaJPiveh6Pb9sXh3%2Bs5Nw6TV8%3D%22%7D; ak_bmsc=5D41EE571C0F0A91FFB635971BEED198~000000000000000000000000000000~YAAQ5NhLF0Jzs62TAQAAZPk8GRoVe0cWHW5+JbMY8BVBDg9dRdjRHN7q0lEKaVjdKiNS0UGq+GPBSjJdSo9I7wADyMG0BmfBRfO2NPj4mTGF9QDebvt0I26VrxaAkyPxXAp0P8CSnpMoHPPTG7EWer2csEes0sU4zowopGvumtBHXA+D/z5JiJ6kqbiGOZOqs/9LAkeHt1KTHfMhv+AvVI1aDRIVX7AwXNl6OiZ1aib5OIYRUImmiFiy9GeNv4huI5JvlUZD7CauC4djuoWwzkT3pqda5xloKyyTtHzvMxSYjnRxezJ8L7Cnwo3Ma/fCW7ukQES/mFiDKmSo0bNv3gkpKj4C7V6r2q9D5/hnaeViVWa+Eg07yt3cXtx9UeOpFr+6UnFF; bm_mi=5FE337C5A2CED4E1CE615DE8DD2E7082~YAAQ5NhLFxies62TAQAAWQM/GRr0C8ca9t+Ebk28hHpZxagozHSeAGlc1jOFpTgIzHIQgsg1jOpjl4yjC5c0zzCEuPouns0XWhzhFp4OP2EfyZtO3p8Zs3pv8Tlre+KIYFO1vj4Ji52hUomeNcUT2FUGtUfNsJU6DadkxS7VvZob8F6AKM/LrxZyOUtM97f8t1WGpN9U/gTYt5BujHM4Tz4/x5+1jnW8/bRMX0zgVaixy6MbXq1ihLZktI/19KP1ccRvpUHa1LUnF9la7SPSdGzDkPlt8VHQ+F1Ohme8toZuWp346MszHP/cbQX41ND2Zs2yyzXQ2MKZttgXqHzGv21lozUQ4+WoTBtXBXXpbbStS6gyoQIR5pssA48Wjv+AbD3wjy4VPwpA+Q1nCtJxhTXhiXv6UTS8PVQElVP7~1; bm_sv=4C040EAF1DB87EB188B616A9B3A7EEA0~YAAQ5NhLFxmes62TAQAAWQM/GRqAVkB/Gpf1tXMUf2yJZjYiz+sXhWrpC2lnSVefccyzyPRQAbaCcHLPnSBqquqjxDOMK/O92Cx8gcLaMUK6LD/MsCsAz/FC5G06w7e2nH7bLXdOW78fO0dZHg0Usfs/H7ZzjaphsDJ/ERuYfLa4b/3CjMlUqn3NrOMRMrmUGv0o8Ylt1VcNMNVt3uPY/bDwzIX1+MUiNYUC9jxJcutNmxUQMLC+/v03t+Oa~1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "TE": "trailers"
}


def retrieve_documents(cik: str):

    cik = cik.zfill(10)  # Ensure CIK is 10 digits with leading zeros

    # Construct the base URL
    base_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    try:
        # Make the GET request
        response = requests.get(base_url, headers=HEADERS)
        
        # Check the status code
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"Error: Received status code {response.status_code} from {base_url}"
            )
        
        # Parse the response JSON
        content = response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    content = content['filings']['recent']
    # elements ['accessionNumber', 'filingDate', 'reportDate', 'acceptanceDateTime', 'act', 'form', 'fileNumber', 'filmNumber', 'items', 'core_type', 'size', 'isXBRL', 'isInlineXBRL', 'primaryDocument', 'primaryDocDescription']

    data = Data()
    for key in content.keys():
        data.__setattr__(key, content[key])

    # we zip all the elements together, and focus only on the cases where form is 10-K
    data = list(zip(data.accessionNumber, 
                    data.filingDate, 
                    data.reportDate, 
                    data.acceptanceDateTime, 
                    data.act, 
                    data.form, 
                    data.fileNumber, 
                    data.filmNumber, 
                    data.items, 
                    data.core_type, 
                    data.size, 
                    data.isXBRL, 
                    data.isInlineXBRL, 
                    data.primaryDocument, 
                    data.primaryDocDescription))
    data = [x for x in data if x[5] == '10-K']

    # keep if report date has year 2022
    data = [x for x in data if x[2].split('-')[0] == '2022']

    # create url to access the document
    data = [f'https://www.sec.gov/Archives/edgar/data/{cik}/{x[0].replace("-", "")}/{x[13]}' for x in data]
    url = data[0]
    # get the url for the -index-headers.html
    url_base = "/".join(url.split("/")[:-1])
    last_element = url.split("/")[-2]

    # convert from 000007297123000071 to
    # 0000072971-23-000071

    last_element = f"{last_element[:10]}-{last_element[10:12]}-{last_element[12:]}"

    url_index = f"{url_base}/{last_element.split('.')[0]}-index-headers.html"

    # read url_index with beautiful soup

    response = requests.get(url_index, headers=HEADERS_HTM)
    # it contains tags, 
    # split <DOCUMENT> and </DOCUMENT> tags
    elements = {}
    text = response.text
    documents = text.split("&lt;DOCUMENT&gt;")

    final_elements = []

    for doc_type in ["10-K", "EX-13"]:
        # keep if documents contain EX-13
        documents_ = [x for x in documents if doc_type in x]

        if not documents_:
            continue

        doc = documents_[-1]
        # split on &gt;
        doc = doc.split("&gt;")[-2]
        # Regular expression to capture text between the first '<' and the last '>'
        pattern = r'<.*>.*</.*?>'
        # Find match
        match = re.search(pattern, doc, re.DOTALL)
        # get text 
        info_a = match.group()
        a_soup = bs(info_a, 'html.parser')
        # find all a 
        as_ = a_soup.find_all('a')
        doc_url = as_[0]['href']
        # complete the url
        doc_url = f"{url_base}/{doc_url}"

        response_ = requests.get(doc_url, headers=HEADERS_HTM)

        content = response_.text
        # split using <hr style="page-break-after:always"/>
        content = content.split('<hr style="page-break-after:always"/>')

        md_texts = []
        pbar = tqdm(content)
        for cont in pbar:
            pbar.set_description(f"Extracting pages from {doc_type}")
            pbar.refresh()
            md_texts.append(md(cont))

        elements[doc_type] = md_texts

    # save as json 

    for key in elements.keys():
        
        pages = elements[key]

        for page in pages:
            # Requesting a classification from the model
            result = yesno(
                f"Is the following document about the Fair Value Estimates for Financial Instruments? Document: {page}"
            )

            # Do something if it's a "Yes"
            if result == 'Yes':
                final_elements.append(page)


    dict_={'pages': final_elements}
    with open(f"pages_{cik}.json", "w") as f:
        json.dump(dict_, f)

#%%
# test
if __name__ == "__main__":
    # Specify the CIK
    cik = "72971"
    retrieve_documents(cik)