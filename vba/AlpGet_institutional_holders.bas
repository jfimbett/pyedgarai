
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