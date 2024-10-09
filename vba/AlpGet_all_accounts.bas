
Function AlpGet_all_accounts(apiUrl As String, apiToken As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim fullUrl As String
    fullUrl = apiUrl & "?api_token=" & apiToken
    
    On Error GoTo ErrorHandler
    http.Open "GET", fullUrl, False
    http.setRequestHeader "accept", "application/json"
    http.send ""
    
    If http.Status = 200 Then
        Dim jsonResponse As String
        jsonResponse = http.responseText
        
        Dim json As Object
        Set json = JsonConverter.ParseJson(jsonResponse)
        
        Dim outputStartingCell As Range
        Set outputStartingCell = Application.Caller
        
        Dim i As Integer
        i = 0
        Dim key As Variant
        For Each key In json.Keys
            Dim column As Integer
            column = 0
            Dim subKey As Variant
            For Each subKey In json(key).Keys
                outputStartingCell.Offset(i, column).Value = json(key)(subKey)
                column = column + 1
            Next subKey
            i = i + 1
        Next key
        Set AlpGet_all_accounts = outputStartingCell
    Else
        MsgBox "Error: " & http.Status & " - " & http.statusText
        Set AlpGet_all_accounts = CVErr(xlErrValue)
    End If
    
    On Error GoTo 0
    Exit Function
    
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description
    Set AlpGet_all_accounts = CVErr(xlErrValue)
End Function


Please ensure you have added the `JsonConverter` module to your VBA project, which can be obtained from the VBA-JSON library (https://github.com/VBA-tools/VBA-JSON) for parsing JSON responses.