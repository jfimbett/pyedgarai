
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