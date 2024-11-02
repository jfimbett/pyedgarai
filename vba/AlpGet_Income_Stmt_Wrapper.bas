
Function AlpGet_Income_Stmt_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim headers As Object
    Dim indexKey As Variant
    Dim colKey As Variant
    Dim row As Long
    Dim col As Long
    
    ' Set the endpoint URL
    url = "http://localhost:5000/income_stmt?ticker=" & ticker & "&api_token=" & api_token

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

    ' Access the data
    Set data = jsonResponse("data")
    Set headers = data("index")
    
    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write column headers
    col = col + 1
    For Each colKey In data.Keys
        If colKey <> "index" Then
            Cells(row, col).Value = colKey
            col = col + 1
        End If
    Next colKey
    col = ActiveCell.Column
    row = row + 1

    ' Write row index and data
    For Each indexKey In headers
        Cells(row, col).Value = indexKey
        col = col + 1
        For Each colKey In data.Keys
            If colKey <> "index" Then
                Cells(row, col).Value = data(colKey)(Application.Match(indexKey, headers, 0))
                col = col + 1
            End If
        Next colKey
        row = row + 1
        col = ActiveCell.Column
    Next indexKey

    AlpGet_Income_Stmt_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Income_Stmt(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Income_Stmt_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Income_Stmt = result
End Function
