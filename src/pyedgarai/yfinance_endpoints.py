#%%
import yfinance as yf
import time
import json
import pandas as pd

if __name__ == '__main__':
    RELATIVE_PATH = ""
    DATA_PATH = "../../data/"
else:
    RELATIVE_PATH = 'src/pyedgarai/' # make this the standard relative path for the project, and only if this file is ran from the root directory we change it. 
    DATA_PATH = "data/"

def get_stock_element(ticker, element):
    stock = yf.Ticker(ticker)
    # element is an attribute
    response =  getattr(stock, element)
    # The return type must be a string, dict, list, tuple with headers or status,
    # convert accordingly to json 

    if isinstance(response, dict) or isinstance(response, list) or isinstance(response, tuple):
        return {"data": response}

    # if its a dataframe convert to json 
    if hasattr(response, 'to_dict'):

        # if index is 0, 1, ... do not transpose
        if not (response.index[0] in range(len(response.index))):
            response = response.T

            # reset index 
            response = response.reset_index()
            
        # go column by column and if not string, or number (e.g. timestamp) convert to string
        for col in response.columns:
            if not response[col].dtype in ['int64', 'float64', 'object']:
                response[col] = response[col].astype(str)

        to_return = response.to_dict(orient='list')

        # if keys are timestamps convert to string
        to_return = {str(k): v for k, v in to_return.items()}

        # if values are timestamp, convert to string 
        for k, v in to_return.items():
            if isinstance(v[0], pd.Timestamp):
                to_return[k] = [str(val) for val in v]
        return json.dumps({"data": to_return})
        
    
    # if its a string return as is
    if isinstance(response, str):
        return {"data": response}
    
    # if its smt else convert it to text first 
    return {"data": str(response)}

def get_stock_elements():
    ticker = 'AAPL'
    stock = yf.Ticker(ticker)
    dirs = dir(stock)
    # remove dunders 
    elements = [d for d in dirs if not d.startswith('__')]
    # remove if starts with one _
    elements = [d for d in elements if not d.startswith('_')]

    implement_elements = []
    implement_functions = []
    for element in elements:
        try:
            time.sleep(0.3)
            getattr(stock, element)

            # if it is a function add to the functions list
            if callable(getattr(stock, element)):
                implement_functions.append(element)
            else:
                implement_elements.append(element)
        except:
            continue

    # store in json 
    elements = {'implemented_elements': implement_elements, 'implemented_functions': implement_functions}
    with open(f'{RELATIVE_PATH}stock_elements.json', 'w') as f:
        json.dump(elements, f)



#get_stock_elements()

# we are going to create the classes for the elements inside of a loop

# %%
# load json 
with open(f'{RELATIVE_PATH}stock_elements.json', 'r') as f:
    elements = json.load(f)

IMPLEMENTED_ELEMENTS = elements['implemented_elements']
IMPLEMENTED_FUNCTIONS = elements['implemented_functions']