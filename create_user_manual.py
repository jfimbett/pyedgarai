# %%
import openai
import os
import time
from tqdm import tqdm
# Specify the environment variable name
api_key_var_name = "OPENAI_API_KEY"

# Check if the environment variable is set
assert api_key_var_name in os.environ, f"Environment variable {api_key_var_name} not found."

# all files in vba/responses 
files = list(os.listdir('vba'))
# keep if they finish in .bas 
files = [file for file in files if file.endswith('.bas')]

#%%
def wrap(i):
    with open(f'vba/{files[i]}', 'r') as f:
        example = f.read()


    client = openai.OpenAI(
            api_key = os.environ.get('OPENAI_API_KEY')
        )

    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    The following .bas file contains two functions (a function and a wrapper) that perform a particular task. 
                    I need you to give me in a html format the user manual for the function. Infer from the code what the function does, and 
                    give examples of its usage. 

                        {example}

                    Use some css inside of the html to make it look nice, you can use for example bootstrap. Also try that the code in the examples you provide look like vba/excel. 
                   

                Only return the html code NOTHING ELSE!
                    """,
                }
            ],
            model="gpt-4o",
        )

    code_text = chat_completion.choices[0].message.content

    # remove the ```vba and the ```
    code_text = code_text.replace('```html', '').replace('```', '')

    # get the function name from the bas file 
    # in example
    function_name = example.split('Function ')[1].split('(')[0]

    # write to a .bas file
    with open(f'vba/user_manual/{function_name}.html', 'w') as f:
        f.write(code_text)
   
    print(f"Manual for {function_name} written to vba/user_manual/{function_name}.html")


for i, file in tqdm(enumerate(files)):
    time.sleep(5)
    wrap(i)
# %%
