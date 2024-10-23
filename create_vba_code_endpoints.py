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

                Since UDF cannot modify cells, we also need to use a wrapper. I will give you an example. The following function connects to the /account endpoint
                Function AlpGet_Account_Wrapper(units As String, account As String, frame As String, taxonomy As String, api_token As String) as String
                ' Add an error handler
                On Error GoTo ErrorHandler
                Dim url As String
                Dim xmlhttp As Object
                Dim jsonResponse As Object
                Dim data As Variant
                Dim row As Long
                Dim col As Long

                ' Set the endpoint URL
                url = "http://127.0.0.1:5000/account?units=" & units & "&account=" & account & "&frame=" & frame & "&taxonomy=" & taxonomy & "&api_token=" & api_token

                ' Create the XMLHTTP object
                Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

                ' Set up the request
                xmlhttp.Open "GET", url, False
                xmlhttp.setRequestHeader "Accept", "application/json"

                ' Send the request
                xmlhttp.Send
                
                ' Parse the JSON response
                Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

                ' Check if 'data' key exists in the response
                If Not jsonResponse.Exists("data") Then Exit Function

                ' Display jsonResponse
                Set data = jsonResponse("data")
                
                row = ActiveCell.Row + 1
                col = ActiveCell.Column
                
                ' Write headers
                Cells(row, col).Value     = "accn"
                Cells(row, col + 1).Value = "cik"
                Cells(row, col + 2).Value = "end"
                Cells(row, col + 3).Value = "entityName"
                Cells(row, col + 4).Value = "loc"
                Cells(row, col + 5).Value = "start"
                Cells(row, col + 6).Value = "val"

                ' Iterate over each item in the 'data' array and write to the sheet
                Dim item As Variant
                For Each item In data
                    row = row + 1
                    Cells(row, col).Value     = item("accn")
                    Cells(row, col + 1).Value = item("cik")
                    Cells(row, col + 2).Value = item("end")
                    Cells(row, col + 3).Value = item("entityName")
                    Cells(row, col + 4).Value = item("loc")
                    Cells(row, col + 5).Value = item("start")
                    Cells(row, col + 6).Value = item("val")
                Next item

                AlpGet_Account_Wrapper = units & "-" & account & "-" & frame & "-" & taxonomy 

            Exit Function
            ErrorHandler:
                MsgBox "An error occurred: " & Err.Description & " " & Erl
                Exit Function   
            End Function

            And the function called from the cell would be 

            Function AlpGet_Account(units As String, account As String, frame As String, taxonomy As String, api_token As String) As String
                Dim result As String
                result = Evaluate("AlpGet_Account_Wrapper(...
                AlpGet_Account = result
            End Function

            Also assume the module JsonConverter is already imported.
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