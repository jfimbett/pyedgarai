# %%
import openai
import os
with open('api_tryout.txt', 'r') as f:
    example = f.read()

# get up to 40 lines 
total_lines = len(example.split('\n'))
cut = 40 if total_lines > 40 else total_lines
example = '\n'.join(example.split('\n')[:cut])

client = openai.OpenAI(
        api_key = os.environ.get('OPENAI_API_KEY')
    )

chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
                   The following text contains the curl to an api endpoint, together with part of the response (if its too long). 
                   Give me the code in VBA to make the same request inside of a function. Each one of the variables in the curl should be passed as arguments to the function. 
                   Start the name of the function with AlpGet_ and the name of the endpoint. The reply of the api endpoint should be then written to the cell where the function has been called. 
                   Now, if the response is a dictionary with different keys, or a list of dictionaries, create then a table starting from the cell where the function has been called.

                     {example}

                Note: return only the code, since I am using the API, and I need to write it to a file. 
                """,
            }
        ],
        model="gpt-4o",
    )

code_text = chat_completion.choices[0].message.content

# remove the ```vba and the ```
code_text = code_text.replace('```vba', '').replace('```', '')

# get the function name in the first line 
function_name = code_text.split('\n')[1].split(' ')[1]
# remove anything after ( 
function_name = function_name.split('(')[0]

# write to a .bas file
with open(f'vba/{function_name}.bas', 'w') as f:
    f.write(code_text)
# %%
print(f"Function {function_name} written to vba/{function_name}.bas")