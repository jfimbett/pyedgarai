
Function AlpGet_QuarterlyIncomeStmt(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    
    Dim url As String
    url = "http://127.0.0.1:5000/quarterly_income_stmt?ticker=" & ticker & "&api_token=" & api_token
    
    On Error GoTo ErrorHandler
    
    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
    End With

    If http.Status = 200 Then
        Dim jsonResponse As String
        jsonResponse = http.responseText
        
        Dim json As Object
        Set json = JsonConverter.ParseJson(jsonResponse)
        
        Dim dataDict As Object
        Set dataDict = json("data")
        
        Dim ws As Worksheet
        Dim startCell As Range
        Set ws = Application.Caller.Worksheet
        Set startCell = Application.Caller
        
        Dim keys As Collection
        Dim key As Variant
        Set keys = New Collection
        
        Dim i As Long
        i = 0
        For Each key In dataDict.Keys
            keys.Add key
            startCell.Offset(0, i).Value = key
            i = i + 1
        Next key
        
        Dim j As Long
        Dim arr As Variant
        Dim dictItem As Variant
        For i = 1 To dataDict(keys(1)).Count
            For j = 1 To keys.Count
                dictItem = dataDict(keys(j))(i - 1)
                If IsObject(dictItem) Then
                    arr = dictItem.Items
                    startCell.Offset(i, j - 1).Value = Join(Application.Transpose(arr), ", ")
                Else
                    startCell.Offset(i, j - 1).Value = dictItem
                End If
            Next j
        Next i
        
        Set json = Nothing
        Set dataDict = Nothing
        Set http = Nothing
        Exit Function
    End If

ErrorHandler:
    AlpGet_QuarterlyIncomeStmt = "Error: " & http.Status & " " & http.statusText
    Set http = Nothing
End Function
