
Function AlpGet_QuarterlyBalanceSheet_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim header As Variant
    Dim i As Long, j As Long
    Dim key As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/quarterly_balancesheet?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'data' key exists in the response
    If Not jsonResponse.Exists("data") Then Exit Function

    ' Display jsonResponse
    Set data = jsonResponse("data")
    header = data.Keys
    
    row = ActiveCell.row
    col = ActiveCell.Column

    ' Write headers
    For j = LBound(header) To UBound(header)
        Cells(row, col + j).Value = header(j)
    Next j
    
    ' Find maximum dimension length
    Dim maxLen As Long
    maxLen = -1
    For Each key In keys(data)
        If IsArray(data(key)) Then
            maxLen = WorksheetFunction.Max(maxLen, UBound(data(key)))
        End If
    Next key
    
    ' Write data to cells
    For i = 0 To maxLen
        row = row + 1
        j = 0
        For Each key In keys(data)
            If IsArray(data(key)) And i <= UBound(data(key)) Then
                Cells(row, col + j).Value = data(key)(i)
            Else
                Cells(row, col + j).Value = data(key)
            End If
            j = j + 1
        Next key
    Next i

    AlpGet_QuarterlyBalanceSheet_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_QuarterlyBalanceSheet(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_QuarterlyBalanceSheet_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_QuarterlyBalanceSheet = result
End Function
