
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
    For Each key In data.Keys
        r.Offset(0, c).Value = key
        c = c + 1
    Next key
    
    ' Populate data
    For i = 0 To UBound(data("index"))
        c = 0
        For Each key In data.Keys
            r.Offset(i + 1, c).Value = data(key)(i)
            c = c + 1
        Next key
    Next i
End Function


This code makes an HTTP GET request to the specified API endpoint, parses the JSON response, and writes the parsed data into a table starting from the cell where the function `AlpGet_QuarterlyBalanceSheet` is called. The function requires two arguments: the `ticker` and `api_token` values.