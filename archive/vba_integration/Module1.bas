Attribute VB_Name = "Module1"

Function AlpGet_Account(units As String, account As String, frame As String, taxonomy As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Account_Wrapper(""" & units & """, """ & account & """, """ & frame & """, """ & taxonomy & """, """ & api_token & """)")
    AlpGet_Account = result
End Function

Function AlpGet_Account_Wrapper(units As String, account As String, frame As String, taxonomy As String, api_token As String) As String
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
    xmlhttp.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'data' key exists in the response
    If Not jsonResponse.Exists("data") Then Exit Function

    ' Display jsonResponse
    Set data = jsonResponse("data")
    
    row = ActiveCell.row + 1
    col = ActiveCell.column
    
    ' Write headers
    Cells(row, col).Value = "accn"
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
        Cells(row, col).Value = item("accn")
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


Function AlpGet_Actions(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim data As Object
    Dim index As Variant
    Dim key As Variant
    Dim arr() As Variant
    Dim r As Integer, c As Integer
    
    ' Create the request URL
    url = "http://127.0.0.1:5000/actions?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Set data = jsonResponse("data")
    
    ' Set the initial cell for output
    Dim startRow As Integer
    Dim startCol As Integer
    startRow = Application.Caller.row
    startCol = Application.Caller.column
    
    ' Write index to the cell
    index = data("index")
    For c = LBound(index) To UBound(index)
        Cells(startRow, startCol + c).Value = index(c)
    Next c
    
    ' Write data to cells
    r = 1
    For Each key In data.keys
        If key <> "index" Then
            Cells(startRow + r, startCol).Value = key
            arr = data(key)
            For c = LBound(arr) To UBound(arr)
                Cells(startRow + r, startCol + 1 + c).Value = arr(c)
            Next c
            r = r + 1
        End If
    Next key
End Function


To use this function, make sure to include a JSON parser like `VBA-JSON` in your environment to handle the `JsonConverter.ParseJson` function. The function will place the data starting from the cell where it's called. It will create a header row with "Dividends" and "Stock Splits" and fill in the subsequent rows with the corresponding data.
Function AlpGet_all_accounts(apiUrl As String, apiToken As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim fullUrl As String
    fullUrl = apiUrl & "?api_token=" & apiToken
    
    On Error GoTo ErrorHandler
    http.Open "GET", fullUrl, False
    http.setRequestHeader "accept", "application/json"
    http.send ""
    
    If http.Status = 200 Then
        Dim jsonResponse As String
        jsonResponse = http.responseText
        
        Dim json As Object
        Set json = JsonConverter.ParseJson(jsonResponse)
        
        Dim outputStartingCell As Range
        Set outputStartingCell = Application.Caller
        
        Dim i As Integer
        i = 0
        Dim key As Variant
        For Each key In json.keys
            Dim column As Integer
            column = 0
            Dim subKey As Variant
            For Each subKey In json(key).keys
                outputStartingCell.Offset(i, column).Value = json(key)(subKey)
                column = column + 1
            Next subKey
            i = i + 1
        Next key
        Set AlpGet_all_accounts = outputStartingCell
    Else
        MsgBox "Error: " & http.Status & " - " & http.statusText
        Set AlpGet_all_accounts = CVErr(xlErrValue)
    End If
    
    On Error GoTo 0
    Exit Function
    
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description
    Set AlpGet_all_accounts = CVErr(xlErrValue)
End Function


Please ensure you have added the `JsonConverter` module to your VBA project, which can be obtained from the VBA-JSON library (https://github.com/VBA-tools/VBA-JSON) for parsing JSON responses.
Function AlpGet_analyst_price_targets(ticker As String, api_token As String)
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/analyst_price_targets?ticker=" & ticker & "&api_token=" & api_token
    
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim response As String
    response = http.responseText
    
    ' Parse the JSON response
    Dim json As Object
    Set json = JsonConverter.ParseJson(response)
    
    Dim data As Variant
    data = json("data")
    
    Dim currentCell As Range
    Set currentCell = Application.Caller

    currentCell.Value = "Current"
    currentCell.Offset(0, 1).Value = data("current")
    
    currentCell.Offset(1, 0).Value = "High"
    currentCell.Offset(1, 1).Value = data("high")
    
    currentCell.Offset(2, 0).Value = "Low"
    currentCell.Offset(2, 1).Value = data("low")
    
    currentCell.Offset(3, 0).Value = "Mean"
    currentCell.Offset(3, 1).Value = data("mean")
    
    currentCell.Offset(4, 0).Value = "Median"
    currentCell.Offset(4, 1).Value = data("median")
    
End Function


Note: This code assumes you have already included a JSON parser module (such as `JsonConverter`) to parse the JSON response. If not, you will need to add one to handle the JSON parsing in VBA.
Function AlpGet_balancesheet(ticker As String, api_token As String)
    Dim http As Object
    Dim jsonResponse As Object
    Dim cell As Range
    Dim i As Long, j As Long
    Dim rowHeaders As Variant
    Dim key As Variant
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    Set cell = Application.Caller

    ' Construct URL
    Dim url As String
    url = "http://127.0.0.1:5000/balancesheet?ticker=" & ticker & "&api_token=" & api_token
    
    ' Make GET request to API
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Retrieve data
    rowHeaders = jsonResponse("data")("index")
    Dim dataKeys As Collection
    Set dataKeys = jsonResponse("data").keys
    
    ' Write headers
    For i = 2 To dataKeys.Count
        cell.Offset(0, i - 1).Value = dataKeys(i)
    Next i

    ' Write index and data
    For i = 0 To UBound(rowHeaders)
        cell.Offset(i + 1, 0).Value = rowHeaders(i + 1)
        For j = 2 To dataKeys.Count
            key = dataKeys(j)
            cell.Offset(i + 1, j - 1).Value = jsonResponse("data")(key)(i + 1)
        Next j
    Next i
End Function


Note: Make sure to include the JSON Converter module in your VBA project to enable JSON parsing. You can download the JSON Converter from: [https://github.com/VBA-tools/VBA-JSON](https://github.com/VBA-tools/VBA-JSON).
Function AlpGet_balance_sheet(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim cell As Range
    Dim headers As Collection
    Dim rowIndex As Long
    Dim columnIndex As Long

    ' Set the API URL with parameters
    url = "http://127.0.0.1:5000/balance_sheet?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the JSON response
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Navigate to the data part of the JSON
    Set data = json("data")

    ' Get the starting cell
    Set cell = Application.Caller

    ' Create headers
    Set headers = New Collection
    For Each key In data.keys
        If key <> "index" Then
            headers.Add key
        End If
    Next key

    ' Write headers to the first row
    columnIndex = 1
    For Each header In headers
        cell.Offset(0, columnIndex).Value = header
        columnIndex = columnIndex + 1
    Next header

    ' Write data to the cells below the header
    For rowIndex = 0 To UBound(data("index"))
        cell.Offset(rowIndex + 1, 0).Value = data("index")(rowIndex)
        columnIndex = 1
        For Each header In headers
            cell.Offset(rowIndex + 1, columnIndex).Value = data(header)(rowIndex)
            columnIndex = columnIndex + 1
        Next header
    Next rowIndex

    ' Return the result
    AlpGet_balance_sheet = "Data written starting from cell " & cell.Address

End Function

Function AlpGet_basic_info(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/basic_info?ticker=" & ticker & "&api_token=" & api_token

    ' Make the HTTP request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    Dim jsonResponse As String
    jsonResponse = http.responseText
    
    ' Parse JSON response using VBA-JSON library
    Dim json As Object
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    Dim keys As Variant
    Dim rowCount As Long
    Dim key As Variant
    
    ' Start position to write response data
    Dim startRow As Long, startCol As Long
    startRow = Application.Caller.row
    startCol = Application.Caller.column
    
    ' Check if the data is a dictionary
    If json.Exists("data") Then
        keys = json("data").keys
        
        rowCount = 0
        For Each key In keys
            Cells(startRow + rowCount, startCol).Value = key
            Cells(startRow + rowCount, startCol + 1).Value = json("data")(key)
            rowCount = rowCount + 1
        Next key
    Else
        ' Simple fallback to write whole JSON response
        Cells(startRow, startCol).Value = jsonResponse
    End If
    
    ' Set the function to return the top-left cell of the table
    AlpGet_basic_info = Cells(startRow, startCol).Value
End Function


Note: To run this code, you'll need to include a JSON parser library for VBA such as `VBA-JSON`.
Function AlpGet_calendar(ticker As String, api_token As String)

    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim cell As Range
    Dim i As Integer
    
    ' Set up HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/calendar?ticker=" & ticker & "&api_token=" & api_token
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get the response
    response = http.responseText
    
    ' Parse JSON
    Set json = JsonConverter.ParseJson(response)
    
    ' Assume the function is called in a worksheet cell
    Set cell = Application.Caller
    
    ' Write keys and values to the worksheet starting from the cell where function is called
    i = 0
    Dim key As Variant
    For Each key In json("data")
        cell.Offset(i, 0).Value = key
        If TypeName(json("data")(key)) = "Collection" Then
            cell.Offset(i, 1).Value = Join(json("data")(key).ToArray, ", ")
        Else
            cell.Offset(i, 1).Value = json("data")(key)
        End If
        i = i + 1
    Next key

End Function


**Note:** This code assumes you have the `JsonConverter` module for VBA, which allows VBA to parse JSON objects. JsonConverter can be added by importing the `JsonConverter.bas` file from [this GitHub repository](https://github.com/VBA-tools/VBA-JSON).
Function AlpGet_CashFlow(ticker As String, api_token As String)

    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/cashflow?ticker=" & ticker & "&api_token=" & api_token
    
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim jsonResponse As String
    jsonResponse = http.responseText
    
    Dim json As Object
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    Dim data As Object
    Set data = json("data")
    
    Dim headers As Collection
    Set headers = New Collection
    
    Dim key As Variant
    Dim index As Integer
    index = 0
    
    ' Add headers (keys) from the dictionary
    For Each key In data.keys
        headers.Add key
        ActiveCell.Offset(0, index).Value = key
        index = index + 1
    Next key
    
    ' Add data (values) to the table
    Dim i As Integer, j As Integer
    For i = 1 To data(0).Count ' Assume each list has the same number of elements
        For j = 1 To headers.Count
            ActiveCell.Offset(i, j - 1).Value = data(headers(j))(i - 1)
        Next j
    Next i

End Function


Note: The `JsonConverter` library must be included in the VBA project to parse JSON responses. You can find this library online and include it as a module. To use this function, call it from a cell in Excel like `=AlpGet_CashFlow("AAPL", "t3stt%40ken")`, and it will write the returned data as a table starting from the cell where the formula is called.
Function AlpGet_cash_flow(apiUrl As String, ticker As String, apiToken As String) As Variant
    Dim http As Object
    Dim url As String
    Dim responseJson As Object
    Dim header As Variant
    Dim data As Variant
    Dim cell As Range
    Dim i As Integer, j As Integer
    
    ' Create HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Build the URL
    url = apiUrl & "/cash_flow?ticker=" & ticker & "&api_token=" & apiToken
    
    ' Make the request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse JSON response
    If http.Status = 200 Then
        Set responseJson = JsonConverter.ParseJson(http.responseText)
        Set cell = Application.Caller
        
        ' Assuming the JSON is structured with "data" as the outer key and contains a dictionary of arrays
        header = responseJson("data").keys
        data = responseJson("data")
        
        ' Output headers
        For i = 0 To UBound(header)
            cell.Offset(0, i).Value = header(i)
        Next i
        
        ' Output data
        For j = 0 To UBound(data(header(0)))
            For i = 0 To UBound(header)
                cell.Offset(j + 1, i).Value = data(header(i))(j)
            Next i
        Next j
    Else
        AlpGet_cash_flow = "Error: " & http.Status & " - " & http.statusText
    End If
End Function

Function AlpGet_cik_names(api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim key As Variant
    Dim rng As Range
    Dim columnIndex As Integer

    ' Initialize the URL
    url = "http://127.0.0.1:5000/cik_names?api_token=" & api_token

    ' Create the WinHttpRequest object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.Open "GET", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "accept", "application/json"

    ' Send the request
    http.send

    ' Get the response
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Determine the starting cell (where the function is called)
    Set rng = Application.Caller

    ' Check if the response is a dictionary
    If VBA.TypeName(json) = "Dictionary" Then
        ' Write JSON keys and values to the table starting from the call cell
        rng.Cells(1, 1).Value = "CIK"
        rng.Cells(1, 2).Value = "Name"
        rowIndex = 2
        For Each key In json.keys
            rng.Cells(rowIndex, 1).Value = key
            rng.Cells(rowIndex, 2).Value = json(key)
            rowIndex = rowIndex + 1
        Next key
    Else
        rng.Value = "Invalid response format"
    End If

    ' Clean up
    Set http = Nothing
    Set json = Nothing
End Function


Note: This code assumes that you have a JSON parser set up in your VBA environment. If you don't have one, you'll need to include a JSON conversion library such as "VBA-JSON" by Tim Hall (https://github.com/VBA-tools/VBA-JSON) to parse the JSON data.
Function AlpGet_cik_sic(api_token As String, endpoint As String) As Variant
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim jsonResponse As Object
    Dim row As Integer
    Dim col As Integer
    Dim key As Variant

    ' Create the URL
    url = endpoint & "?api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")

    ' Initialize the HTTP request
    On Error GoTo ErrorHandler
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Get the response
    response = http.responseText

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(response)
    
    ' Determine the start position for table output
    row = Application.Caller.row
    col = Application.Caller.column

    ' Write the JSON keys and values to cells
    For Each key In jsonResponse
        Cells(row, col).Value = key
        Cells(row, col + 1).Value = jsonResponse(key)
        row = row + 1
    Next key

    Exit Function

ErrorHandler:
    MsgBox "Error in API call: " & Err.Description
End Function


To use the above function, you will need a JSON parser library for VBA, such as the `JsonConverter` module. You can find and import this module from its repository on GitHub to handle JSON parsing:

1. JSON converter module: https://github.com/VBA-tools/VBA-JSON

Import the JsonConverter module into your VBA project to enable JSON parsing.
Function AlpGet_cik_tickers(api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    Dim url As String
    url = "http://127.0.0.1:5000/cik_tickers?api_token=" & api_token
    
    ' Initialize the request
    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
    End With
    
    ' Check if the request was successful
    If http.Status = 200 Then
        ' Parse JSON response
        Dim json As Object
        Set json = JsonConverter.ParseJson(http.responseText)
        
        Dim cell As Range
        Set cell = Application.Caller
        Dim row As Long
        row = 0

        Dim key As Variant
        For Each key In json.keys
            cell.Offset(row, 0).Value = key
            cell.Offset(row, 1).Value = Join(json(key), ", ")
            row = row + 1
        Next key
    Else
        ' Handle error
        MsgBox "Error: " & http.Status & " - " & http.statusText
    End If
    
    Set http = Nothing
End Function


**Note**: Make sure to include the `JsonConverter` module in your VBA project to parse JSON responses. You can find the VBA JSON Converter library online and import it into your VBA project before running the function.
Function AlpGet_clean_name(api_url As String, name As String, api_token As String)
    Dim http As Object
    Dim json As Object
    Dim result As String
    Dim cell As Range
    Dim url As String

    ' Concatenate the URL with parameters
    url = api_url & "?name=" & name & "&api_token=" & api_token

    ' Create a new XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Open a connection to the API endpoint
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    
    ' Send the request
    http.send

    ' Get the response
    result = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(result)

    ' Get the current cell
    Set cell = Application.Caller

    ' Check if the JSON object contains the expected key
    If json.Exists("clean_name") Then
        ' Output the clean_name value to the cell
        cell.Value = json("clean_name")
    End If

    ' Clean up
    Set http = Nothing
    Set json = Nothing
End Function

Function AlpGet_CompanyFacts(cik As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim cell As Range
    Dim startCell As Range
    Dim i As Long, j As Long
    Dim keys As Object
    Dim dict As Object
    Dim subDict As Object
    Dim units As Object
    Dim item As Object
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/company_facts?cik=" & cik & "&api_token=" & api_token
    
    ' Send HTTP request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get response text
    response = http.responseText
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(response)
    
    ' Get the starting cell
    Set startCell = Application.Caller
    
    ' If response is a dictionary or a list of dictionaries, create a table
    If VarType(json) = vbObject Then
        Set keys = json.keys
        ' Assuming the response is a dictionary with the top-level keys being "cik", "entityName", "facts"
        i = 0
        For Each key In keys
            Set dict = json(key)
            If TypeName(dict) = "Dictionary" And key = "facts" Then
                For Each subKey In dict.keys
                    Set subDict = dict(subKey)
                    If TypeName(subDict) = "Dictionary" Then
                        For Each unitKey In subDict("units").keys
                            Set units = subDict("units")(unitKey)
                            For Each item In units
                                ' Write the table headers
                                If i = 0 Then
                                    For j = 0 To item.Count - 1
                                        startCell.Offset(0, j).Value = item.keys(j)
                                    Next j
                                End If
                                ' Write each row of data
                                For j = 0 To item.Count - 1
                                    startCell.Offset(i + 1, j).Value = item.Items(j)
                                Next j
                                i = i + 1
                            Next item
                        Next unitKey
                    End If
                Next subKey
            Else
                ' Write single value responses directly to the cell
                startCell.Offset(0, i).Value = CStr(json(key))
            End If
        Next key
    Else
        ' If response is a single value, write it directly to the cell
        startCell.Value = CStr(json)
    End If
    
    Set AlpGet_CompanyFacts = response

Cleanup:
    Set http = Nothing
    Set json = Nothing
    Set keys = Nothing
    Set dict = Nothing
    Set subDict = Nothing
    Set units = Nothing
End Function


Ensure that "JsonConverter" is included in your VBA project to parse JSON correctly. You can get "JsonConverter" from https://github.com/VBA-tools/VBA-JSON.
Function AlpGet_company_concept(cik As String, tag As String, taxonomy As String, api_token As String)

    ' Set variables
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim dict As Object
    Dim i As Long
    Dim col As Long
    Dim resultRow As Long
    Dim cell As Range
    
    ' Create the URL
    url = "http://127.0.0.1:5000/company_concept?cik=" & cik & "&tag=" & tag & "&taxonomy=" & taxonomy & "&api_token=" & api_token
    
    ' Set reference to the current cell where the formula is called
    Set cell = Application.Caller
    
    ' Create the XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Open the request
    http.Open "GET", url, False
    
    ' Set the request headers
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Write JSON data to Excel
    If Not jsonResponse Is Nothing Then
        ' Handle the main keys of the response if needed
        data = jsonResponse("units")("USD")
        
        ' Create headers
        col = 0
        If TypeName(data) = "Collection" And data.Count > 0 Then
            For Each dict In data
                For Each key In dict.keys
                    cell.Offset(0, col).Value = key
                    col = col + 1
                Next key
                Exit For
            Next dict
            
            ' Fill data
            resultRow = 1
            For Each dict In data
                col = 0
                For Each key In dict.keys
                    cell.Offset(resultRow, col).Value = dict(key)
                    col = col + 1
                Next key
                resultRow = resultRow + 1
            Next dict
        End If
        
    End If

End Function


Note: This code assumes you have a JSON parser available, such as `JsonConverter.bas`, which you can find in various open-source VBA JSON parsers online. You need to include this or a similar JSON parsing library in your VBA project for the above function to work.
Function AlpGet_comparables(cik As String, _
                            method As String, _
                            api_token As String, _
                            industry_digits As Integer, _
                            size_interval As Integer, _
                            profitability_interval As Integer, _
                            growth_rate_interval As Integer, _
                            capital_structure_interval As Integer) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim cell As Range
    Dim key As Variant
    Dim jsonData As Variant
    Dim headers As Variant
    Dim i As Integer

    ' Construct the API request URL
    url = "http://127.0.0.1:5000/comparables?" & _
          "cik=" & cik & _
          "&variables_to_compare=industry" & _
          "&variables_to_compare=size" & _
          "&variables_to_compare=profitability" & _
          "&variables_to_compare=growth_rate" & _
          "&variables_to_compare=capital_structure" & _
          "&variables_to_compare=location" & _
          "&extra_variables=GrossProfit" & _
          "&extra_variables=NetIncomeLoss" & _
          "&extra_variables=EarningsPerShareBasic" & _
          "&method=" & method & _
          "&api_token=" & api_token & _
          "&industry_digits=" & industry_digits & _
          "&size_interval=" & size_interval & _
          "&profitability_interval=" & profitability_interval & _
          "&growth_rate_interval=" & growth_rate_interval & _
          "&capital_structure_interval=" & capital_structure_interval

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    http.send

    ' Validate response status
    If http.Status <> 200 Then
        AlpGet_comparables = "Error: " & http.statusText
        Exit Function
    End If

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)

    ' Write the data to Excel starting at the current cell
    Set cell = Application.Caller
    i = 0
    If TypeName(jsonResponse) = "Dictionary" Then
        headers = jsonResponse.keys
        
        ' Write the headers
        For Each key In headers
            cell.Offset(0, i).Value = key
            i = i + 1
        Next key

        ' Write the data rows
        i = 0
        For Each key In headers
            cell.Offset(1, i).Value = jsonResponse(key)("0")
            i = i + 1
        Next key
    End If

    ' Cleanup
    Set http = Nothing
    Set jsonResponse = Nothing
End Function


Function AlpGet_dividends(ticker As String, api_token As String)
    Dim url As String
    Dim xhr As Object
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim i As Long
    Dim startCell As Range

    ' Construct the URL
    url = "http://127.0.0.1:5000/dividends?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHttpRequest object
    Set xhr = CreateObject("MSXML2.ServerXMLHTTP.6.0")

    ' Make the HTTP GET request
    xhr.Open "GET", url, False
    xhr.setRequestHeader "accept", "application/json"
    xhr.send

    ' Get the response
    response = xhr.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(response)
    Set data = json("data")

    ' Get the starting cell where the function is called
    Set startCell = Application.Caller

    ' Write the headers
    startCell.Offset(0, 0).Value = "Date"
    startCell.Offset(0, 1).Value = "Dividends"

    ' Write the data to the cells
    For i = 1 To data("Date").Count
        startCell.Offset(i, 0).Value = data("Date")(i)
        startCell.Offset(i, 1).Value = data("Dividends")(i)
    Next i
End Function


Make sure you have a JSON parser for VBA, such as the "JsonConverter" module from VBA-JSON, for the `JsonConverter.ParseJson` function to work. You can download it from GitHub and include it in your VBA project.
Function AlpGet_earnings_dates(ticker As String, api_token As String)
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Construct the API endpoint URL
    Dim url As String
    url = "http://127.0.0.1:5000/earnings_dates?ticker=" & ticker & "&api_token=" & api_token

    ' Open the request
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send

    ' Process the response
    Dim jsonResponse As Object
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Dim data As Object
    Set data = jsonResponse("data")
    
    ' Write the response to the worksheet
    Dim startCell As Range
    Set startCell = Application.Caller
    Dim index As Variant
    Dim dateKey As Variant
    
    ' Write header row
    For Each index In data("index")
        startCell.Offset(0, 1).Value = index
        Set startCell = startCell.Offset(0, 1)
    Next index

    ' Write data rows
    Set startCell = Application.Caller
    For Each dateKey In data.keys
        If dateKey <> "index" Then
            startCell.Value = dateKey
            Dim values As Variant
            values = data(dateKey)
            Dim i As Integer
            For i = LBound(values) To UBound(values)
                startCell.Offset(0, i + 1).Value = values(i)
            Next i
            Set startCell = startCell.Offset(1, 0)
        End If
    Next dateKey
End Function


This function assumes that a JSON parsing library like `VBA-JSON` is available in your VBA environment (`JsonConverter.bas` should be imported into your VBA project for `JsonConverter.ParseJson`). Adjust references and imports as necessary for your environment.
Function AlpGet_earnings_estimate(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    Dim url As String
    url = "http://127.0.0.1:5000/earnings_estimate?ticker=" & ticker & "&api_token=" & api_token

    ' Making the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parsing JSON response
    Dim jsonResponse As Object
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)

    ' Writing response to Excel cell
    Dim ws As Worksheet
    Set ws = Application.Caller.Worksheet
    Dim startCell As Range
    Set startCell = Application.Caller

    Dim data As Object
    Set data = jsonResponse("data")

    Dim index As Variant
    Dim keys As Variant
    Dim i As Long, j As Long

    index = data("index")
    keys = data.keys

    ' Write column headers
    For i = LBound(index) To UBound(index)
        ws.Cells(startCell.row, startCell.column + i).Value = index(i)
    Next i

    ' Write data to table
    j = 1
    For Each key In keys
        If key <> "index" Then
            ws.Cells(startCell.row + j, startCell.column).Value = key
            For i = LBound(data(key)) To UBound(data(key))
                ws.Cells(startCell.row + j, startCell.column + i + 1).Value = data(key)(i)
            Next i
            j = j + 1
        End If
    Next key
    
    AlpGet_earnings_estimate = "Data Imported"
End Function


Please make sure you have added the "JsonConverter.bas" module to your VBA project, which you can find on GitHub here: [VBA-JSON](https://github.com/VBA-tools/VBA-JSON). This module is necessary for parsing the JSON response. Additionally, you might need to handle any runtime errors that could arise from network issues or JSON parsing errors.
Function AlpGet_earnings_history(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim ws As Worksheet
    Dim cell As Range
    Dim data As Variant
    Dim i As Long, j As Long
    
    ' Create an instance of the WinHttpRequest.5.1 object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    ' Format the URL with the provided ticker and api_token
    url = "http://127.0.0.1:5000/earnings_history?ticker=" & ticker & "&api_token=" & api_token
    
    ' Open the HTTP request
    http.Open "GET", url, False
    ' Set the request header for JSON response
    http.setRequestHeader "accept", "application/json"
    ' Send the HTTP request
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Set the starting cell for the output (the cell where the function was called)
    Set ws = Application.Caller.Worksheet
    Set cell = Application.Caller
    
    ' Get the data dictionary from the JSON response
    If Not jsonResponse Is Nothing Then
        ' Ensure the response has "data"
        If Not jsonResponse("data") Is Nothing Then
            ' Convert the "data" object to a 2D array for easier processing
            data = jsonResponse("data")
            
            ' Loop through the JSON response keys
            j = 0
            For Each key In data
                ' Write the date/time key
                cell.Offset(0, j).Value = key
                i = 1
                ' Write the corresponding values for the key
                For Each Value In data(key)
                    cell.Offset(i, j).Value = Value
                    i = i + 1
                Next Value
                j = j + 1
            Next key
        End If
    End If
End Function


Make sure to include a JSON parser in your VBA environment, such as `JsonConverter`, which you can find at: https://github.com/VBA-tools/VBA-JSON. This parser is necessary for handling JSON responses in VBA.
Function AlpGet_eps_revisions(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim key As Variant
    Dim arr() As Variant
    Dim i As Integer
    Dim j As Integer

    ' Create a new XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Construct the URL
    url = "http://127.0.0.1:5000/eps_revisions?ticker=" & ticker & "&api_token=" & api_token
    
    ' Make the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get the response
    jsonResponse = http.responseText
    
    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Navigate to the appropriate section of the JSON
    Set data = json("data")
    
    ' Determine the size of the table
    Dim rowCount As Integer
    Dim colCount As Integer
    rowCount = data("index").Count
    colCount = 0
    For Each key In data
        colCount = colCount + 1
    Next key
    
    ' Initialize the array
    ReDim arr(rowCount, colCount)
    
    ' Fill the array with data
    i = 0
    For Each key In data
        j = 0
        For Each Val In data(key)
            If IsNull(Val) Then
                arr(j, i) = "null"
            Else
                arr(j, i) = Val
            End If
            j = j + 1
        Next Val
        i = i + 1
    Next key
    
    ' Output to the sheet
    Dim rng As Range
    Set rng = Application.Caller
    ' Write headers
    For i = 0 To colCount - 1
        rng.Offset(0, i).Value = key
    Next i
    ' Write data
    For j = 0 To rowCount - 1
        For i = 0 To colCount - 1
            rng.Offset(j + 1, i).Value = arr(j, i)
        Next i
    Next j
    
End Function


Please ensure that you have a JSON parser like `JsonConverter` installed in your VBA environment. You can find `JsonConverter` by searching for "VBA JSON parser" online and follow the instructions to install it in your VBA project.
Function AlpGet_eps_trend(ticker As String, api_token As String)

    Dim http As Object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    Dim url As String
    url = "http://127.0.0.1:5000/eps_trend?ticker=" & ticker & "&api_token=" & api_token
    
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim response As String
    response = http.responseText

    Dim json As Object
    Set json = JsonConverter.ParseJson(response)
    
    Dim rowIndex As Integer
    Dim colIndex As Integer
    Dim key As Variant
    Dim arrIndex As Variant
    Dim cell As Range
    Set cell = Application.Caller
    
    ' Output table headers
    colIndex = 0
    For Each key In json("data")
        cell.Offset(0, colIndex).Value = key
        colIndex = colIndex + 1
    Next key
    
    ' Output table data
    rowIndex = 1
    For arrIndex = 0 To UBound(json("data")("index"))
        colIndex = 0
        For Each key In json("data")
            cell.Offset(rowIndex, colIndex).Value = json("data")(key)(arrIndex)
            colIndex = colIndex + 1
        Next key
        rowIndex = rowIndex + 1
    Next arrIndex
    
End Function


**Note**: This code uses `JsonConverter`, a popular VBA JSON library. Ensure you have included this library in your VBA project for JSON parsing. It can be found at: https://github.com/VBA-tools/VBA-JSON
Function AlpGet_fast_info(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim i As Integer
    Dim header As Range

    ' Initialize the URL
    url = "http://127.0.0.1:5000/fast_info?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHttpRequest object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Open the request
    http.Open "GET", url, False

    ' Set the request headers
    http.setRequestHeader "accept", "application/json"

    ' Send the request
    http.send

    ' Get the response text
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Check if response is a dictionary
    If TypeName(json) = "Dictionary" Then
        ' Get the starting cell
        Set header = Application.Caller

        ' Loop through the keys
        i = 0
        For Each key In json.keys
            ' Write key to cell
            header.Offset(0, i).Value = key
            ' Write value to cell
            header.Offset(1, i).Value = json(key)
            i = i + 1
        Next key
    End If
End Function


**Note:** This code requires a JSON parser for VBA. You can use the JSON conversion library by adding the module "JsonConverter.bas" to your project. It can be found in various VBA JSON repositories like [VBA-JSON](https://github.com/VBA-tools/VBA-JSON).
Function AlpGet_financials(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim jsonResponse As Object
    Dim ws As Worksheet
    Dim cell As Range
    Dim dataDict As Object
    Dim dataKey As Variant
    Dim dataArray As Variant
    Dim i As Long, j As Long
    
    ' Initialize HTTP Request
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Construct URL
    url = "http://127.0.0.1:5000/financials?ticker=" & ticker & "&api_token=" & api_token
    
    ' Send GET Request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get Response
    response = http.responseText
    
    ' Parse JSON Response
    Set jsonResponse = JsonConverter.ParseJson(response)
    Set dataDict = jsonResponse("data")
    
    ' Identify the starting cell for output
    Set ws = Application.Caller.Worksheet
    Set cell = Application.Caller
    
    ' Write the headers
    j = 0
    For Each dataKey In dataDict
        cell.Offset(0, j).Value = dataKey
        j = j + 1
    Next dataKey
    
    ' Write the data
    dataArray = dataDict("index")
    For i = LBound(dataArray) To UBound(dataArray)
        j = 0
        For Each dataKey In dataDict
            cell.Offset(i + 1, j).Value = dataDict(dataKey)(i)
            j = j + 1
        Next dataKey
    Next i
End Function


Make sure to add the JSON parser module (`JsonConverter`) to your VBA project for JSON decoding to work correctly. You can find popular JSON parsers like "JsonConverter" by Tim Hall on GitHub, which will allow you to parse JSON objects easily.
Function AlpGet_growth_estimates(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/growth_estimates?ticker=" & ticker & "&api_token=" & api_token

    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
        Dim response As String
        response = .responseText
    End With

    Dim json As Object
    Set json = JsonConverter.ParseJson(response)
    
    Dim row As Long, col As Long
    Dim headers As Collection
    Dim data As Collection

    Set headers = json("data")("index")
    row = Application.Caller.row
    col = Application.Caller.column

    ' Write headers to the sheet
    Dim header As Variant
    For Each header In headers
        Cells(row, col).Value = header
        col = col + 1
    Next header

    ' Write data to the sheet
    Dim key As Variant
    For Each key In json("data").keys
        col = Application.Caller.column
        row = row + 1
        Cells(row, col).Value = key
        Set data = json("data")(key)
        Dim item As Variant
        For Each item In data
            col = col + 1
            If IsNull(item) Then
                Cells(row, col).Value = "NaN"
            Else
                Cells(row, col).Value = item
            End If
        Next item
    Next key
End Function


**Note**: You will need a JSON parser library in VBA, such as the "JsonConverter" library, to handle the JSON response. You can find the `JsonConverter.bas` module through open source repositories like GitHub. Add it to your VBA project before using this code.
Function AlpGet_incomestmt(ticker As String, api_token As String)

    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim jsonData As Object
    
    ' Create HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Set URL
    url = "http://127.0.0.1:5000/incomestmt?ticker=" & ticker & "&api_token=" & api_token
    
    ' Initialize HTTP request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Set jsonData = jsonResponse("data")
    
    ' Write to Excel
    Dim ws As Worksheet
    Set ws = Application.Caller.Worksheet
    
    Dim r As Long, c As Long
    r = Application.Caller.row
    c = Application.Caller.column
    
    Dim key As Variant
    Dim colIndex As Long
    colIndex = 0

    ' Write headers
    For Each key In jsonData.keys
        ws.Cells(r, c + colIndex).Value = key
        colIndex = colIndex + 1
    Next key

    ' Find maximum number of rows
    Dim maxRows As Long
    maxRows = 0
    For Each key In jsonData.keys
        If UBound(jsonData(key)) > maxRows Then
            maxRows = UBound(jsonData(key))
        End If
    Next key

    ' Write data
    Dim rowIndex As Long
    For rowIndex = 1 To maxRows + 1
        colIndex = 0
        For Each key In jsonData.keys
            If rowIndex <= UBound(jsonData(key)) + 1 Then
                ws.Cells(r + rowIndex, c + colIndex).Value = jsonData(key)(rowIndex - 1)
            End If
            colIndex = colIndex + 1
        Next key
    Next rowIndex

    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
    Set jsonData = Nothing

End Function


**Note:** The code assumes that you have a JSON parsing library, such as `JsonConverter` (which you can find as a downloadable `.bas` file on various VBA-related websites), referenced into your VBA environment. Make sure to include that parsing library, as VBA does not include native JSON parsing.
Function AlpGet_income_stmt(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim key As Variant
    Dim r As Integer, c As Integer

    ' Initialize variables
    url = "http://127.0.0.1:5000/income_stmt?ticker=" & ticker & "&api_token=" & api_token
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Make HTTP GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get response
    response = http.responseText
    Set json = JsonConverter.ParseJson(response)
    Set data = json("data")

    ' Write response to cells
    r = Application.Caller.row
    c = Application.Caller.column
    For Each key In data.keys
        Cells(r, c).Value = key
        Cells(r, c).Offset(1, 0).Resize(1, UBound(data(key)) + 1).Value = Application.WorksheetFunction.Transpose(data(key))
        c = c + 1
    Next key
End Function


Note: This code assumes that you have included a JSON parser module, such as `JsonConverter`, in your VBA project. You can find this tool on GitHub as `VBA-JSON` and follow the instructions there to include it in your VBA environment.
Function AlpGet_info(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    Dim url As String
    url = "http://127.0.0.1:5000/info?ticker=" & ticker & "&api_token=" & api_token

    ' Open the request
    http.Open "GET", url, False
    
    ' Set request headers
    http.setRequestHeader "accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Check for successful response
    If http.Status = 200 Then
        Dim jsonResponse As String
        jsonResponse = http.responseText
        
        ' Parse JSON response (requires reference to Microsoft Scripting Runtime)
        Dim jsonParser As Object
        Set jsonParser = JsonConverter.ParseJson(jsonResponse)
        
        Dim dataObj As Object
        Set dataObj = jsonParser("data")
        
        ' Determine the first cell of output
        Dim ws As Worksheet
        Set ws = Application.Caller.Worksheet
        
        Dim startRow As Long
        Dim startCol As Long
        startRow = Application.Caller.row
        startCol = Application.Caller.column
        
        Dim i As Long
        i = startRow

        Dim key As Variant
        For Each key In dataObj.keys
            If TypeName(dataObj(key)) = "Collection" Then
                ' Handle list of dictionaries (array of objects)
                Dim j As Long
                j = 0
                Dim item As Object
                For Each item In dataObj(key)
                    Dim subKey As Variant
                    Dim col As Long
                    col = startCol
                    For Each subKey In item.keys
                        ws.Cells(i + j, col).Value = subKey
                        ws.Cells(i + j + 1, col).Value = item(subKey)
                        col = col + 1
                    Next subKey
                    j = j + 2 ' double increment to separate sets
                Next item
            Else
                ' Handle simple key-value pairs
                ws.Cells(i, startCol).Value = key
                ws.Cells(i, startCol + 1).Value = dataObj(key)
                i = i + 1
            End If
        Next key
        
        AlpGet_info = "Data written successfully."
    Else
        AlpGet_info = "Error: " & http.Status & " " & http.statusText
    End If
    
    Set http = Nothing
End Function

Function AlpGet_InsiderTransactions(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim xml As Object
    Dim http As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim cell As Range
    Dim r As Long, c As Long

    url = "http://127.0.0.1:5000/insider_transactions?ticker=" & ticker & "&api_token=" & api_token

    Set xml = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    Set http = CreateObject("MSXML2.DOMDocument")
    
    xml.Open "GET", url, False
    xml.setRequestHeader "accept", "application/json"
    xml.send

    If xml.Status = 200 Then
        Set jsonResponse = JsonConverter.ParseJson(xml.responseText)
        
        If Not jsonResponse Is Nothing Then
            Set data = jsonResponse("data")
            Set cell = Application.Caller.Cells(1, 1)
            
            r = 0
            For Each key In data.keys
                c = 0
                cell.Offset(r, c).Value = key
                c = c + 1
                For Each item In data(key)
                    cell.Offset(r, c).Value = item
                    c = c + 1
                Next item
                r = r + 1
            Next key
        End If
    Else
        AlpGet_InsiderTransactions = "Error: " & xml.Status & " - " & xml.statusText
    End If

End Function

Note: To run this code, you will need a JSON parser for VBA, such as the `JsonConverter` module, which you can get from the VBA-JSON library.
Function AlpGet_insider_purchases(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As String
    Dim json As Object
    Dim cell As Range
    Dim i As Integer
    Dim j As Integer
    
    url = "http://127.0.0.1:5000/insider_purchases?ticker=" & ticker & "&api_token=" & api_token

    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"
    xmlhttp.send

    jsonResponse = xmlhttp.responseText
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    Set cell = Application.Caller

    ' Determine if response is a dictionary with keys or list of dictionaries
    Dim dataKeys As Object
    Set dataKeys = json("data").keys

    ' Write keys to the top row of the table
    For i = 1 To dataKeys.Count
        cell.Offset(0, i - 1).Value = dataKeys(i - 1)
    Next i

    ' Write data values to the table
    Dim maxCount As Integer
    maxCount = 0
    For Each key In dataKeys
        maxCount = WorksheetFunction.Max(maxCount, UBound(json("data")(key)))
    Next key
    
    For i = 1 To maxCount
        For j = 1 To dataKeys.Count
            cell.Offset(i, j - 1).Value = json("data")(dataKeys(j - 1))(i - 1)
        Next j
    Next i
   
    ' Return nothing as data is written to cells
    AlpGet_insider_purchases = "Data retrieved and written to cells."
    
    Set xmlhttp = Nothing
    Set json = Nothing
End Function

Function AlpGet_insider_roster_holders(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim jsonResponse As Object
    Dim data As Object
    Dim dictKey As Variant
    Dim cell As Range
    Dim rowOffset As Long
    Dim columnOffset As Long
    Dim i As Long

    ' Set URL
    url = "http://127.0.0.1:5000/insider_roster_holders?ticker=" & ticker & "&api_token=" & api_token

    ' Create HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the response
    response = http.responseText
    
    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(response)
    
    ' Extract data object
    Set data = jsonResponse("data")
    
    ' Write data to worksheet starting from the cell where the function is called
    Set cell = Application.Caller
    rowOffset = 0

    ' Write headers
    For Each dictKey In data.keys
        cell.Offset(rowOffset, columnOffset).Value = dictKey
        columnOffset = columnOffset + 1
    Next dictKey

    rowOffset = rowOffset + 1
    columnOffset = 0
    
    ' Write data for each key in the dictionary
    For i = 1 To data("Name").Count
        columnOffset = 0
        For Each dictKey In data.keys
            cell.Offset(rowOffset, columnOffset).Value = data(dictKey)(i)
            columnOffset = columnOffset + 1
        Next dictKey
        rowOffset = rowOffset + 1
    Next i
    
    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
    Set data = Nothing
End Function


To correctly parse JSON in VBA, you'll need a JSON parsing library like "VBA-JSON" by Tim Hall. Make sure you have it imported and set up in your VBA environment.
Function AlpGet_institutional_holders(ticker As String, api_token As String)
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/institutional_holders?ticker=" & ticker & "&api_token=" & api_token
    
    ' Send GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse the JSON response
    Dim jsonResponse As Object
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Check if the cell where the function is called is part of a range or a single cell
    Dim ws As Worksheet
    Dim startCell As Range
    Set startCell = Application.Caller
    
    ' Output values into the sheet
    Dim data As Object
    Set data = jsonResponse("data")
    
    Dim headers As Variant
    headers = Array("Date Reported", "Holder", "pctHeld", "Shares", "Value")
    
    Dim i As Long, j As Long
    
    ' Write headers
    For j = LBound(headers) To UBound(headers)
        startCell.Offset(0, j).Value = headers(j)
    Next j
    
    ' Write data
    Dim n As Long
    n = UBound(data(headers(0)))

    For i = 0 To n
        For j = LBound(headers) To UBound(headers)
            startCell.Offset(i + 1, j).Value = data(headers(j))(i)
        Next j
    Next i
End Function


Make sure to include the `JsonConverter` module in your VBA project to parse JSON responses. You can get it from https://github.com/VBA-tools/VBA-JSON.
Function AlpGet_isin(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim responseData As Variant
    Dim cell As Range
    
    ' Construct URL with parameters
    url = "http://127.0.0.1:5000/isin?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create a new XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Initialize request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Parse the response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Write output to the cell where the function is called
    Set cell = Application.Caller
    
    ' Check if the response contains data
    If Not jsonResponse Is Nothing Then
        If VBA.TypeName(jsonResponse) = "Collection" Then
            If jsonResponse.Exists("data") Then
                cell.Value = jsonResponse("data")
            End If
        Else
            cell.Value = http.responseText
        End If
    End If
    
    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
    Set cell = Nothing
End Function


Note: This script uses a JSON parser. To use it, you might need to import a JSON library, such as VBA-JSON (https://github.com/VBA-tools/VBA-JSON), into your VBA project in order to use `JsonConverter.ParseJson`.
Function AlpGet_major_holders(ticker As String, api_token As String)
    Dim url As String
    Dim http As Object
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim headers As Object
    Dim r As Range
    Dim c As Long
    
    ' Construct the URL
    url = "http://127.0.0.1:5000/major_holders?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP request object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Send the GET request
    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
        response = .responseText
    End With
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(response)
    Set data = json("data")
    
    ' Writing data to the spreadsheet
    Set r = Application.Caller
    c = 0
    For Each headers In data
        r.Offset(0, c).Value = headers
        r.Offset(1, c).Value = data(headers)(1)
        c = c + 1
    Next headers
    
End Function


Function AlpGet_mutualfund_holders(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim field As Variant
    Dim currentRow As Integer
    Dim i As Integer
    Dim key As Variant

    ' Create the URL with parameters
    url = "http://127.0.0.1:5000/mutualfund_holders?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Send the GET request
    With http
        .Open "GET", url, False
        .setRequestHeader "Accept", "application/json"
        .send
        response = .responseText
    End With
    
    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(response)
    
    ' Get the data dictionary
    Set data = json("data")
    
    ' Write the data to the Excel sheet
    currentRow = Application.Caller.row
    i = 0
    For Each key In data.keys
        ' Write the headers
        Cells(currentRow, Application.Caller.column + i).Value = key
        ' Write the data under each header
        For Each field In data(key)
            Cells(currentRow + 1, Application.Caller.column + i).Value = field
            currentRow = currentRow + 1
        Next field
        currentRow = Application.Caller.row
        i = i + 1
    Next key
End Function


Note: To use the above function, you will need to import the "JsonConverter" library into your VBA environment to handle JSON parsing. You can do this by including the `JsonConverter.bas` file from https://github.com/VBA-tools/VBA-JSON.
Function AlpGet_news(ticker As String, api_token As String) As String
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim item As Object
    Dim i As Integer
    Dim cell As Range
    
    ' Get the current cell location
    Set cell = Application.Caller

    ' Create the URL with passed arguments
    url = "http://127.0.0.1:5000/news?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the JSON response
    jsonResponse = http.responseText
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Accessing the data array from the JSON
    Set data = json("data")
    
    ' Initialize column headers
    cell.Offset(0, 0).Value = "Title"
    cell.Offset(0, 1).Value = "Publisher"
    cell.Offset(0, 2).Value = "Link"
    cell.Offset(0, 3).Value = "Type"
    
    ' Looping through the items and filling in the Excel cells
    i = 1
    For Each item In data
        cell.Offset(i, 0).Value = item("title")
        cell.Offset(i, 1).Value = item("publisher")
        cell.Offset(i, 2).Value = item("link")
        cell.Offset(i, 3).Value = item("type")
        i = i + 1
    Next item
End Function


**Notes:**

- The code uses an external JSON parser (like "JsonConverter.bas"), which needs to be imported into your VBA project for parsing JSON.
- You can obtain "JsonConverter.bas" from reputable sources like GitHub.
- This function assumes that the JSON response has the same structure as shown. Adjust the fields accordingly if the JSON structure changes.
Function AlpGet_options(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim dataArray As Variant
    Dim i As Integer

    ' Initialize the URL with passed parameters
    url = "http://127.0.0.1:5000/options?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Make the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Check if "data" key exists in the response
    If Not jsonResponse("data") Is Nothing Then
        ' Convert the data to an array
        dataArray = jsonResponse("data")

        ' Output the array as a table starting at the called cell
        For i = LBound(dataArray) To UBound(dataArray)
            ActiveCell.Offset(i, 0).Value = dataArray(i)
        Next i
    Else
        ActiveCell.Value = "No data available"
    End If

    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
End Function


Note: Make sure to have the JSON parser code (like `JsonConverter.bas`) imported in your VBA environment to use the `JsonConverter.ParseJson` function. JSON parsing libraries can be found on platforms like GitHub, such as `VBA-JSON`.
Function AlpGet_QuarterlyBalanceSheet(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim responseText As String
    Dim jsonResponse As Object
    Dim data As Object
    Dim r As Range
    Dim c As Long, i As Long
    
    ' Set the URL with query parameters
    url = "http://127.0.0.1:5000/quarterly_balance_sheet?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create a new HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Make the request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get the response text
    responseText = http.responseText
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(responseText)
    
    ' Get the data part of the response
    Set data = jsonResponse("data")
    
    ' Initialize output starting cell
    Set r = Application.Caller

    ' Populate headers
    c = 0
    For Each key In data.keys
        r.Offset(0, c).Value = key
        c = c + 1
    Next key
    
    ' Populate data
    For i = 0 To UBound(data("index"))
        c = 0
        For Each key In data.keys
            r.Offset(i + 1, c).Value = data(key)(i)
            c = c + 1
        Next key
    Next i
End Function


This code makes an HTTP GET request to the specified API endpoint, parses the JSON response, and writes the parsed data into a table starting from the cell where the function `AlpGet_QuarterlyBalanceSheet` is called. The function requires two arguments: the `ticker` and `api_token` values.
Function AlpGet_QuarterlyFinancials(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonData As Object
    Dim dict As Object
    Dim i As Integer
    Dim j As Integer
    
    ' Set the URL
    url = "http://127.0.0.1:5000/quarterly_financials?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get the JSON response
    jsonResponse = http.responseText
    
    ' Parse the JSON response
    Set jsonData = JsonConverter.ParseJson(jsonResponse)
    
    ' Check if JSON data is available and contains "data"
    If Not jsonData Is Nothing And Not jsonData("data") Is Nothing Then
        Set dict = jsonData("data")
        
        ' Write the table headers
        j = 0
        For Each key In dict
            ThisWorkbook.Sheets(1).Cells(1, j + 1).Value = key
            j = j + 1
        Next key
        
        ' Write the data
        i = 0
        For Each key In dict
            j = 1
            If IsArray(dict(key)) Then
                For Each Value In dict(key)
                    If IsObject(Value) Then
                        ThisWorkbook.Sheets(1).Cells(j + 1, i + 1).Value = "Object"
                    Else
                        ThisWorkbook.Sheets(1).Cells(j + 1, i + 1).Value = Value
                    End If
                    j = j + 1
                Next Value
            End If
            i = i + 1
        Next key
    End If
    
    Set jsonData = Nothing
    Set http = Nothing
End Function


**Note:** Before you can successfully use this code, you'll need to add a JSON parser to your VBA environment. One commonly used library is `JsonConverter`, which you can find on GitHub under VBA tools for JSON parsing (search for `VBA-JSON`). Include `JsonConverter` in your project to enable JSON parsing. Additionally, adjust the sheet reference `Sheets(1)` as needed.
Function AlpGet_QuarterlyIncomeStmt(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    
    Dim url As String
    url = "http://127.0.0.1:5000/quarterly_income_stmt?ticker=" & ticker & "&api_token=" & api_token
    
    On Error GoTo ErrorHandler
    
    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
    End With

    If http.Status = 200 Then
        Dim jsonResponse As String
        jsonResponse = http.responseText
        
        Dim json As Object
        Set json = JsonConverter.ParseJson(jsonResponse)
        
        Dim dataDict As Object
        Set dataDict = json("data")
        
        Dim ws As Worksheet
        Dim startCell As Range
        Set ws = Application.Caller.Worksheet
        Set startCell = Application.Caller
        
        Dim keys As Collection
        Dim key As Variant
        Set keys = New Collection
        
        Dim i As Long
        i = 0
        For Each key In dataDict.keys
            keys.Add key
            startCell.Offset(0, i).Value = key
            i = i + 1
        Next key
        
        Dim j As Long
        Dim arr As Variant
        Dim dictItem As Variant
        For i = 1 To dataDict(keys(1)).Count
            For j = 1 To keys.Count
                dictItem = dataDict(keys(j))(i - 1)
                If IsObject(dictItem) Then
                    arr = dictItem.Items
                    startCell.Offset(i, j - 1).Value = Join(Application.Transpose(arr), ", ")
                Else
                    startCell.Offset(i, j - 1).Value = dictItem
                End If
            Next j
        Next i
        
        Set json = Nothing
        Set dataDict = Nothing
        Set http = Nothing
        Exit Function
    End If

ErrorHandler:
    AlpGet_QuarterlyIncomeStmt = "Error: " & http.Status & " " & http.statusText
    Set http = Nothing
End Function

Function AlpGet_quarterly_balancesheet(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim rowIndex As Integer, columnIndex As Integer
    Dim key As Variant
    Dim dataArray() As Variant
    Dim headers As Collection

    ' Initialize the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Construct the URL
    url = "http://127.0.0.1:5000/quarterly_balancesheet?ticker=" & ticker & "&api_token=" & api_token

    ' Make the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the response
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Get the data from the JSON response
    Set headers = New Collection
    rowIndex = Application.ThisCell.row
    columnIndex = Application.ThisCell.column

    ' Extract data and headers
    For Each key In json("data").keys
        headers.Add key
    Next key

    ' Set headers in the first row
    For Each key In headers
        Cells(rowIndex, columnIndex).Value = key
        columnIndex = columnIndex + 1
    Next key

    ' Write data starting from the second row
    ReDim dataArray(1 To UBound(json("data")(headers(1))) + 1, 1 To headers.Count)
    
    ' Loop over the JSON data and place values in the array
    For rowIndex = 1 To UBound(json("data")(headers(1))) + 1
        For columnIndex = 1 To headers.Count
            dataArray(rowIndex, columnIndex) = json("data")(headers(columnIndex))(rowIndex - 1)
        Next columnIndex
    Next rowIndex

    ' Output the data to the worksheet starting at the cell where the function is called
    Application.ThisCell.Offset(1, 0).Resize(UBound(dataArray, 1), UBound(dataArray, 2)).Value = dataArray
End Function


Make sure to include a reference to the JSON converter (`JsonConverter.bas`) in your VBA project, which you can find online, for handling JSON parsing in VBA.
Function AlpGet_quarterly_cashflow(ticker As String, api_token As String)
    Dim httpRequest As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonData As Object
    Dim i As Integer, j As Integer
    Dim headerKeys As Collection
    Dim dataValues As Variant
    
    ' Create the HTTP request object
    Set httpRequest = CreateObject("MSXML2.XMLHTTP")
    
    ' Set the URL with the provided parameters
    url = "http://127.0.0.1:5000/quarterly_cashflow?ticker=" & ticker & "&api_token=" & api_token
    
    ' Open the request and set the headers
    httpRequest.Open "GET", url, False
    httpRequest.setRequestHeader "accept", "application/json"
    
    ' Send the request and get the response text
    httpRequest.send
    jsonResponse = httpRequest.responseText
    
    ' Parse the JSON response
    Set jsonData = JsonConverter.ParseJson(jsonResponse)
    
    ' Get header keys
    Set headerKeys = New Collection
    For Each key In jsonData("data").keys
        headerKeys.Add key
    Next key
    
    ' Write headers to the worksheet
    For j = 1 To headerKeys.Count
        Cells(1, j).Value = headerKeys(j)
    Next j
    
    ' Write data to the worksheet
    dataValues = jsonData("data")(headerKeys(1)) ' Just getting the length
    For i = 1 To UBound(dataValues) + 1
        For j = 1 To headerKeys.Count
            Cells(i + 1, j).Value = jsonData("data")(headerKeys(j))(i - 1)
        Next j
    Next i
End Function


Ensure you have the JSON parser library (`JsonConverter`) available in your VBA environment, or you can find a library like `VBA-JSON` online to handle JSON parsing in VBA.
Function AlpGet_quarterly_cash_flow(ticker As String, api_token As String)
    Dim url As String
    Dim http As Object
    Dim jsonResponse As String
    Dim json As Object
    Dim ws As Worksheet
    Dim i As Long, j As Long
        
    ' Set the API URL
    url = "http://127.0.0.1:5000/quarterly_cash_flow?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Make the request
    With http
        .Open "GET", url, False
        .setRequestHeader "Accept", "application/json"
        .send
        jsonResponse = .responseText
    End With
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Get the worksheet and starting cell
    Set ws = Application.Caller.Worksheet
    Dim startCell As Range
    Set startCell = Application.Caller
    
    ' Write the table header
    Dim headers As Collection
    Set headers = json("data").keys
    For j = 1 To headers.Count
        startCell.Offset(0, j - 1).Value = headers(j)
    Next j
    
    ' Write the table data
    Dim dataIndex As Collection
    Set dataIndex = json("data")("index")
    
    For i = 1 To dataIndex.Count
        startCell.Offset(i, 0).Value = dataIndex(i)
        For j = 2 To headers.Count
            startCell.Offset(i, j - 1).Value = json("data")(headers(j))(i)
        Next j
    Next i
    
    Set http = Nothing
    Set json = Nothing
End Function

Function AlpGet_Quarterly_IncomeStmt(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim i As Long, j As Long
    Dim headers As Collection
    Dim header As Variant

    ' Create the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/quarterly_incomestmt?ticker=" & ticker & "&api_token=" & api_token
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse the JSON response
    jsonResponse = http.responseText
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Extract data from JSON
    Set data = json("data")

    ' Set headers for the table
    Set headers = New Collection
    For Each header In data
        headers.Add header
    Next header

    ' Write headers to Excel
    For j = 1 To headers.Count
        ActiveCell.Offset(0, j - 1).Value = headers(j)
    Next j

    ' Determine the number of data rows
    Dim numRows As Long
    numRows = data(headers(1)).Count

    ' Write data to Excel
    For i = 1 To numRows
        For j = 1 To headers.Count
            If Not IsNull(data(headers(j))(i)) Then
                ActiveCell.Offset(i, j - 1).Value = data(headers(j))(i)
            Else
                ActiveCell.Offset(i, j - 1).Value = "NaN"
            End If
        Next j
    Next i
End Function


### Note

- The code uses a JSON parser (`JsonConverter.ParseJson`) available in VBA, which requires adding a JSON parsing library. You can download and add the `JsonConverter.bas` to your VBA project to enable JSON parsing.
- To add the JSON parser, you should download it from a trusted source such as [VBA-JSON](https://github.com/VBA-tools/VBA-JSON) and import it into your VBA project.
- Change the `ActiveCell` reference as needed depending on where you want the data to be written in your Excel sheet.
Function AlpGet_recommendations(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim jsonResponse As Object
    Dim baseUrl As String
    Dim url As String
    Dim ws As Worksheet
    Dim cell As Range
    Dim jsonData As Object
    Dim i As Long
    Dim key As Variant
    Dim headerRow As Range
    Dim firstCell As Range

    ' Set the worksheet and initial cell
    Set ws = Application.Caller.Worksheet
    Set cell = Application.Caller
    Set firstCell = cell

    ' Initialize HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    
    ' Create the URL for the API request
    baseUrl = "http://127.0.0.1:5000/recommendations"
    url = baseUrl & "?ticker=" & ticker & "&api_token=" & api_token
    
    ' Make the request to the API
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Set jsonData = jsonResponse("data")

    ' Write headers
    For Each key In jsonData.keys
        cell.Value = key
        Set cell = cell.Offset(0, 1)
    Next key
    
    ' Write data
    Set headerRow = ws.Range(firstCell, cell.Offset(-1, -1))
    For i = 1 To jsonData("period").Count
        Set cell = firstCell.Offset(i, 0)
        For Each key In jsonData.keys
            cell.Value = jsonData(key)(i - 1)
            Set cell = cell.Offset(0, 1)
        Next key
    Next i

    Set AlpGet_recommendations = headerRow
End Function


Note: To use the JSON parsing function `JsonConverter.ParseJson`, you need to include a JSON library in your VBA project. A common choice is to use "JsonConverter" which you can download from this [GitHub repository](https://github.com/VBA-tools/VBA-JSON) and add to your VBA project.
Function AlpGet_RecommendationsSummary(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim cell As Range
    Dim headers As Variant
    Dim data As Variant
    Dim i As Integer
    Dim j As Integer
    
    ' Construct the URL with the provided arguments
    url = "http://127.0.0.1:5000/recommendations_summary?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Get the starting cell
    Set cell = Application.Caller
    
    ' Prepare headers from the JSON keys
    headers = Array("period", "strongBuy", "buy", "hold", "sell", "strongSell")
    
    ' Write headers to the sheet
    For i = LBound(headers) To UBound(headers)
        cell.Offset(0, i).Value = headers(i)
    Next i
    
    ' Write data to the sheet
    data = jsonResponse("data")
    
    For i = 0 To UBound(data("period"))
        For j = LBound(headers) To UBound(headers)
            cell.Offset(i + 1, j).Value = data(headers(j))(i)
        Next j
    Next i

    ' Return the response to the calling cell
    AlpGet_RecommendationsSummary = "Data written to the sheet"
End Function


Make sure you have a JSON parser, such as `JsonConverter.bas` from VBA-JSON, imported into your VBA environment to allow the JSON parsing to work.
Function AlpGet_revenue_estimate(api_url As String, ticker As String, api_token As String) As Variant
    Dim requestUrl As String
    Dim httpRequest As Object
    Dim jsonResponse As String
    Dim jsonResponseObj As Object
    Dim dataObj As Object
    Dim indexArray As Variant
    Dim period As Variant
    Dim i As Integer, j As Integer
    
    ' Construct the request URL
    requestUrl = api_url & "?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the HTTP request
    Set httpRequest = CreateObject("MSXML2.XMLHTTP")
    httpRequest.Open "GET", requestUrl, False
    httpRequest.setRequestHeader "accept", "application/json"
    httpRequest.send
    
    ' Get the response
    jsonResponse = httpRequest.responseText
    
    ' Parse the JSON response
    Set jsonResponseObj = JsonConverter.ParseJson(jsonResponse)
    Set dataObj = jsonResponseObj("data")
    
    ' Get index array
    indexArray = dataObj("index")
    
    ' Write the table to Excel starting from the cell where the function is called
    With Application.Caller
        ' Write header row
        For j = LBound(indexArray) To UBound(indexArray)
            .Offset(0, j).Value = indexArray(j)
        Next j
        
        ' Write data rows
        i = 1
        For Each period In dataObj.keys
            If period <> "index" Then
                .Offset(i, 0).Value = period
                For j = LBound(dataObj(period)) To UBound(dataObj(period))
                    .Offset(i, j + 1).Value = dataObj(period)(j)
                Next j
                i = i + 1
            End If
        Next period
    End With
    
End Function

Make sure to include a JSON parsing library like "JsonConverter" (which can be found on GitHub) to parse the API's JSON response.
Function AlpGet_sec_filings(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim jsonResponse As Object
    Dim dataArray As Variant
    Dim i As Integer, j As Integer
    Dim headers As String
    Dim dataObj As Object
    Dim baseRow As Long
    Dim baseCol As Long

    ' Create XMLHTTP Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Construct URL based on input parameters
    Dim url As String
    url = "http://127.0.0.1:5000/sec_filings?ticker=" & ticker & "&api_token=" & api_token
    
    ' Send GET request to the API
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    dataArray = jsonResponse("data")
    
    ' Determine the starting point of the table in Excel
    baseRow = Application.Caller.row
    baseCol = Application.Caller.column
    
    ' Extract headers
    headers = Array("date", "edgarUrl", "epochDate", "maxAge", "title", "type", "exhibits_8-K", "exhibits_EXCEL", "exhibits_EX-3.2")
    
    ' Write headers to the worksheet
    For j = 0 To UBound(headers)
        Cells(baseRow, baseCol + j).Value = headers(j)
    Next j
    
    ' Write data to the worksheet
    For i = LBound(dataArray) To UBound(dataArray)
        j = 0
        Cells(baseRow + 1 + i, baseCol + j).Value = dataArray(i)("date")
        Cells(baseRow + 1 + i, baseCol + j + 1).Value = dataArray(i)("edgarUrl")
        Cells(baseRow + 1 + i, baseCol + j + 2).Value = dataArray(i)("epochDate")
        Cells(baseRow + 1 + i, baseCol + j + 3).Value = dataArray(i)("maxAge")
        Cells(baseRow + 1 + i, baseCol + j + 4).Value = dataArray(i)("title")
        Cells(baseRow + 1 + i, baseCol + j + 5).Value = dataArray(i)("type")
        
        If Not IsEmpty(dataArray(i)("exhibits")) Then
            If dataArray(i)("exhibits")("8-K") <> Empty Then
                Cells(baseRow + 1 + i, baseCol + j + 6).Value = dataArray(i)("exhibits")("8-K")
            End If
            If dataArray(i)("exhibits")("EXCEL") <> Empty Then
                Cells(baseRow + 1 + i, baseCol + j + 7).Value = dataArray(i)("exhibits")("EXCEL")
            End If
            ' Additionally check for "EX-3.2" if exists
            If dataArray(i)("exhibits").Exists("EX-3.2") Then
                Cells(baseRow + 1 + i, baseCol + j + 8).Value = dataArray(i)("exhibits")("EX-3.2")
            End If
        End If
    Next i
    
    AlpGet_sec_filings = "Data Retrieved"

    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
End Function

Note: This code assumes that you have added or are using a JSON parsing library, such as "VBA-JSON" for handling JSON data in VBA. You should add the necessary library reference to your VBA project to use `JsonConverter.ParseJson`.
Function AlpGet_splits(ticker As String, api_token As String)
    Dim httpReq As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonData As Object
    Dim cell As Range
    Dim rowCount As Integer
    Dim i As Integer
    
    url = "http://127.0.0.1:5000/splits?ticker=" & ticker & "&api_token=" & api_token

    Set httpReq = CreateObject("MSXML2.XMLHTTP")
    httpReq.Open "GET", url, False
    httpReq.setRequestHeader "accept", "application/json"
    httpReq.send

    jsonResponse = httpReq.responseText

    ' Parse JSON response
    Set jsonData = JsonConverter.ParseJson(jsonResponse)
    
    Set cell = Application.Caller
    rowCount = UBound(jsonData("data")("Date")) + 1

    ' Write headers
    cell.Value = "Date"
    cell.Offset(0, 1).Value = "Stock Splits"
    
    ' Write data to cells
    For i = 0 To rowCount - 1
        cell.Offset(i + 1, 0).Value = jsonData("data")("Date")(i + 1)
        cell.Offset(i + 1, 1).Value = jsonData("data")("Stock Splits")(i + 1)
    Next i
End Function


Note: To run this function successfully, you will need to include a JSON parsing library into your VBA environment. The suggested library is "VBA-JSON" which can be found on GitHub and needs to be referenced in your VBA project.
Function AlpGet_stocks_data(tickers As String, start_date As String, end_date As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim json As String
    Dim jsonResponse As Object
    Dim data As Variant
    Dim i As Long
    Dim cell As Range
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/stocks_data?tickers=" & tickers & "&start_date=" & start_date & "&end_date=" & end_date & "&api_token=" & api_token
    
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    http.send
    
    json = http.responseText
    Set jsonResponse = JsonConverter.ParseJson(json)
    
    If IsObject(jsonResponse) Then
        ' Assuming jsonResponse("data")("Adj Close") is a list of numbers
        data = jsonResponse("data")("Adj Close")
        
        Set cell = Application.Caller
        For i = LBound(data) To UBound(data)
            cell.Offset(i, 0).Value = data(i)
        Next i
    End If
End Function


Note: you 'll need to include a JSON parser library in VBA, such as VBA-JSON, to use the `JsonConverter.ParseJson` function. You can find this library online and follow instructions to import it into your VBA project.
Function AlpGet_submission_history(cik As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    
    Dim endpoint As String
    endpoint = "http://127.0.0.1:5000/submission_history?cik=" & cik & "&api_token=" & api_token
    
    http.Open "GET", endpoint, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim jsonResponse As String
    jsonResponse = http.responseText
    
    ' Parse JSON response
    Dim json As Object
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Get the starting cell
    Dim startCell As Range
    Set startCell = Application.Caller
    
    ' Handle the response as a dictionary
    Dim row As Integer
    Dim col As Integer
    row = 0
    col = 0
    
    Dim key As Variant
    For Each key In json.keys
        startCell.Offset(row, col).Value = key
        row = row + 1
        
        If TypeName(json(key)) = "Collection" Then
            Dim subKey As Variant
            Dim subDict As Object
            Set subDict = json(key)
            
            For Each subKey In subDict.keys
                col = col + 1
                startCell.Offset(row, col).Value = subKey
                startCell.Offset(row + 1, col).Value = subDict(subKey)
            Next
            
            row = row + 2
            col = 0
        Else
            startCell.Offset(row, col).Value = json(key)
        End If
    Next key
    
    Set http = Nothing
    Set json = Nothing
End Function


Note: Make sure you have included a reference to "Microsoft Scripting Runtime" and have a JSON parser module like "JsonConverter" available in your VBA project (e.g. by using the JSON VBA library from GitHub).
Function AlpGet_Sustainability(ticker As String, api_token As String)
    Dim http As Object
    Dim jsonResponse As Object
    Dim jsonData As Object
    Dim cellRow As Long
    Dim cellColumn As Long
    Dim item As Variant
    Dim key As Variant
    
    ' Initialize the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", "http://127.0.0.1:5000/sustainability?ticker=" & ticker & "&api_token=" & api_token, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)("data")
    
    ' Get the position of the function call in the worksheet
    cellRow = Application.Caller.row
    cellColumn = Application.Caller.column
    
    ' Check if the response is a dictionary or contains sub-dictionaries
    If jsonResponse.Count > 0 Then
        Dim tableRow As Long
        tableRow = cellRow
        
        ' Iterate through the keys and values of the JSON object
        For Each key In jsonResponse.keys
            ' Check if the value is an array or dictionary
            If VarType(jsonResponse(key)) = vbObject Then
                ' Iterate through the sub-dictionary or array
                For Each item In jsonResponse(key)
                    ' Print key and value to cells
                    Cells(tableRow, cellColumn).Value = key
                    Cells(tableRow, cellColumn + 1).Value = item
                    tableRow = tableRow + 1
                Next item
            Else
                ' Print key and value to cells
                Cells(tableRow, cellColumn).Value = key
                Cells(tableRow, cellColumn + 1).Value = jsonResponse(key)
                tableRow = tableRow + 1
            End If
        Next key
    End If
End Function


To use this code, make sure you have a JSON parsing library like `JsonConverter.bas` from VBA-JSON in your project. The function requires the ticker and api_token arguments to make the request. The response is parsed and written as a table starting from the cell where the function is placed.
Function AlpGet_upgrades_downgrades(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonObject As Object
    Dim data As Object
    Dim index As Variant
    Dim i As Long, j As Long

    ' Initialize the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Define the API URL
    url = "http://127.0.0.1:5000/upgrades_downgrades?ticker=" & ticker & "&api_token=" & api_token
    
    ' Send the GET request
    With http
        .Open "GET", url, False
        .setRequestHeader "Accept", "application/json"
        .send
        jsonResponse = .responseText
    End With

    ' Parse the JSON response
    Set jsonObject = JsonConverter.ParseJson(jsonResponse)
    Set data = jsonObject("data")
    index = data("index")

    ' Write the headers to the worksheet
    For j = LBound(index) To UBound(index)
        ActiveCell.Offset(0, j).Value = index(j)
    Next j

    ' Write the data to the worksheet
    i = 1
    For Each entry In data.keys
        If entry <> "index" Then
            For j = LBound(data(entry)) To UBound(data(entry))
                ActiveCell.Offset(i, j).Value = data(entry)(j)
            Next j
            i = i + 1
        End If
    Next entry
End Function


Function AlpGet_valuation_metrics(api_url As String, tickers As String, api_token As String)

    ' Set up variables
    Dim http As Object
    Dim jsonResp As Object
    Dim json As Object
    Dim vars As Object
    Dim cell As Range
    Dim i As Integer, key As Variant

    ' Initialize HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Construct request URL
    Dim requestUrl As String
    requestUrl = api_url & "/valuation_metrics?tickers=" & tickers & "&api_token=" & api_token

    ' Initialize request
    With http
        .Open "GET", requestUrl, False
        .setRequestHeader "accept", "application/json"
        .send
    End With

    ' Parse JSON response
    Set jsonResp = JsonConverter.ParseJson(http.responseText)

    ' Set the starting point for writing the response
    Set cell = Application.Caller

    If Not jsonResp Is Nothing Then

        ' Handle "avg_multiples"
        Set json = jsonResp("avg_multiples")
        If Not json Is Nothing Then
            i = 0
            For Each key In json.keys
                cell.Offset(i, 0).Value = key
                cell.Offset(i, 1).Value = json(key)
                i = i + 1
            Next key

            ' Move starting cell down by the number of avg_multiples to start the variables table
            Set cell = cell.Offset(i + 1, 0)
        End If

        ' Handle "variables"
        Set vars = jsonResp("variables")
        If Not vars Is Nothing Then
            ' Write headers
            i = 0
            For Each key In vars(1).keys    ' Assumes all dictionaries have the same keys
                cell.Offset(0, i).Value = key
                i = i + 1
            Next key

            ' Write values
            i = 1
            For Each json In vars
                Dim j As Integer
                j = 0
                For Each key In json.keys
                    cell.Offset(i, j).Value = json(key)
                    j = j + 1
                Next key
                i = i + 1
            Next json
        End If

    End If

    ' Cleanup
    Set http = Nothing
    Set jsonResp = Nothing
    Set json = Nothing
    
End Function



