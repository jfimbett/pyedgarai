
Function AlpGet_Quarterly_IncomeStmt_Wrapper(ticker As String, api_token As String) As String
    ' Error handling
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim key As Variant
    Dim index As Variant
    Dim i As Long, j As Long

    ' Constructing the URL
    url = "http://localhost:5000/quarterly_incomestmt?ticker=" & ticker & "&api_token=" & api_token

    ' Creating and setting up the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Sending the request and parsing the response
    xmlhttp.send
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'data' key exists in the response
    If jsonResponse.Exists("data") Then
        Set data = jsonResponse("data")
        
        ' Starting point for output
        Dim startRow As Long
        Dim startCol As Long
        startRow = ActiveCell.Row
        startCol = ActiveCell.Column

        ' Writing headers
        j = 0
        For Each key In data.Keys
            Cells(startRow + 1, startCol + j).Value = key
            j = j + 1
        Next key

        ' Writing data
        If data("index") Is Nothing Then Exit Function
        For i = LBound(data("index")) To UBound(data("index"))
            Cells(startRow + 2 + i, startCol).Value = data("index")(i)
            j = 1
            For Each key In data.Keys
                If key <> "index" Then
                    Cells(startRow + 2 + i, startCol + j).Value = data(key)(i)
                    j = j + 1
                End If
            Next key
        Next i
    End If

    AlpGet_Quarterly_IncomeStmt_Wrapper = ticker & "-" & api_token
    Exit Function

ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_Quarterly_IncomeStmt(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Quarterly_IncomeStmt_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Quarterly_IncomeStmt = result
End Function
