#%%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
from tqdm import tqdm

#%%

def get_data(divs, i):
    divs[i].click()
    time.sleep(5)
    # find element with class try-out and click
    try_out = driver.find_elements(By.CLASS_NAME, "try-out")
    try_out[-1].click()
    time.sleep(5)

    # class execute-wrapper
    execute = driver.find_elements(By.CLASS_NAME, "execute-wrapper")
    execute[-1].click()
    time.sleep(5)
    # search for class copy-to-clipboard
    texts = driver.find_elements(By.CLASS_NAME, "curl-command")
    copy_to_clipboard = texts[-1]
    file_info = ''
    # print text 
    file_info += copy_to_clipboard.text
    codes = driver.find_elements(By.CLASS_NAME, "highlight-code")
    file_info += '\n \n \n'
    codes_ = [code.text.split("\n")[1:] for code in codes]
    file_info += '\n'.join(codes_[-3])

    name_file = divs[i].text.split('\n')[1][1:]
    with open(f'vba/responses/{i}{name_file}.txt', 'w') as f:
        f.write(file_info)

if __name__ == "__main__":
    driver = webdriver.Firefox()

    #go go http://localhost:5000/openapi/swagger

    driver.get("http://localhost:5000/openapi/swagger")

    driver.implicitly_wait(30)

    # get all divs with class opblock-summary-path-description-wrapper
    # we are clicking one by one 

    divs = driver.find_elements(By.CLASS_NAME, "operation-tag-content")

    for i in tqdm(range(len(divs))):
        if i <= 12:
            continue
        try:
            driver = webdriver.Firefox()

            #go go http://localhost:5000/openapi/swagger

            driver.get("http://localhost:5000/openapi/swagger")

            driver.implicitly_wait(30)

            # get all divs with class opblock-summary-path-description-wrapper
            # we are clicking one by one 

            divs = driver.find_elements(By.CLASS_NAME, "operation-tag-content")

            get_data(divs, i)

            driver.close()
        
        except Exception as e:
            print(e)
            driver.close()



# %%
