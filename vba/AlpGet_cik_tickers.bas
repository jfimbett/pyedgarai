
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
        For Each key In json.Keys
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