
Function AlpGet_quarterly_income_stmt_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim item As Variant
    Dim headers As Variant
    Dim i As Integer
    Dim row As Long
    Dim col As Long
    
    ' Set the endpoint URL
    url = "http://localhost:5000/quarterly_income_stmt?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'data' exists
    If Not jsonResponse.Exists("data") Then Exit Function

    ' Display jsonResponse in a table format
    Set data = jsonResponse("data")
    headers = data.Keys
    
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write header
    For i = 0 To UBound(headers)
        Cells(row, col + i).Value = headers(i)
    Next i
    
    ' Write data
    Dim maxLen As Integer
    maxLen = 0
    
    ' Find max length of data lists
    For Each item In data
        If Not IsEmpty(item) Then
            If UBound(item) > maxLen Then
                maxLen = UBound(item)
            End If
        End If
    Next item
    
    Dim j As Integer
    For j = 0 To maxLen
        For i = 0 To UBound(headers)
            On Error Resume Next ' handle cases where there is no j-th value
            Cells(row + j + 1, col + i).Value = data(headers(i))(j)
            On Error GoTo ErrorHandler
        Next i
    Next j

    AlpGet_quarterly_income_stmt_Wrapper = ticker

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_quarterly_income_stmt(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_quarterly_income_stmt_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_quarterly_income_stmt = result
End Function
