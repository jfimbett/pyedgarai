
Function AlpGet_cash_flow(apiUrl As String, ticker As String, apiToken As String) As Variant
    Dim http As Object
    Dim url As String
    Dim responseJson As Object
    Dim header As Variant
    Dim data As Variant
    Dim cell As Range
    Dim i As Integer, j As Integer
    
    ' Create HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Build the URL
    url = apiUrl & "/cash_flow?ticker=" & ticker & "&api_token=" & apiToken
    
    ' Make the request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse JSON response
    If http.Status = 200 Then
        Set responseJson = JsonConverter.ParseJson(http.responseText)
        Set cell = Application.Caller
        
        ' Assuming the JSON is structured with "data" as the outer key and contains a dictionary of arrays
        header = responseJson("data").keys
        data = responseJson("data")
        
        ' Output headers
        For i = 0 To UBound(header)
            cell.Offset(0, i).Value = header(i)
        Next i
        
        ' Output data
        For j = 0 To UBound(data(header(0)))
            For i = 0 To UBound(header)
                cell.Offset(j + 1, i).Value = data(header(i))(j)
            Next i
        Next j
    Else
        AlpGet_cash_flow = "Error: " & http.Status & " - " & http.statusText
    End If
End Function
