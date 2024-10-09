
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