
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
    http.Send
    
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


Note: You'll need to include a JSON parser library in VBA, such as VBA-JSON, to use the `JsonConverter.ParseJson` function. You can find this library online and follow instructions to import it into your VBA project.