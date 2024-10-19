
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
    Set headers = json("data").Keys
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
