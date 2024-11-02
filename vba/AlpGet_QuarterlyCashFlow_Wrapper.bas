
Function AlpGet_QuarterlyCashFlow_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long
    Dim key As Variant

    ' Set the endpoint URL
    url = "http://localhost:5000/quarterly_cashflow?ticker=" & ticker & "&api_token=" & api_token

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
    
    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers
    Dim keys As Collection
    Set keys = data.Keys
    Dim header As Variant
    Dim i As Long

    ' Write column headers
    i = 0
    For Each header In keys
        Cells(row, col + i).Value = header
        i = i + 1
    Next header

    ' Write data rows
    Dim index As Variant
    For Each index In data("index")
        row = row + 1
        Cells(row, col).Value = index
        i = 1
        For Each key In keys
            If key <> "index" Then
                Cells(row, col + i).Value = IIf(IsNull(data(key)(index)), "", data(key)(index))
                i = i + 1
            End If
        Next key
    Next index

    AlpGet_QuarterlyCashFlow_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_QuarterlyCashFlow(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_QuarterlyCashFlow_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_QuarterlyCashFlow = result
End Function
