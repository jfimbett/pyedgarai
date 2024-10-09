
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
    cellRow = Application.Caller.Row
    cellColumn = Application.Caller.Column
    
    ' Check if the response is a dictionary or contains sub-dictionaries
    If jsonResponse.Count > 0 Then
        Dim tableRow As Long
        tableRow = cellRow
        
        ' Iterate through the keys and values of the JSON object
        For Each key In jsonResponse.Keys
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