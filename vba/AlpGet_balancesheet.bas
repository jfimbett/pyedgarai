
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
    http.Send

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