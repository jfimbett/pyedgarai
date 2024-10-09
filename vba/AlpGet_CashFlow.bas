
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