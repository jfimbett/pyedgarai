
Function AlpGet_Actions_Wrapper(ticker As String, api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/actions?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value = "Date"
    Cells(row, col + 1).Value = "Dividends"
    Cells(row, col + 2).Value = "Stock Splits"
    
    Dim key As Variant
    For Each key In data.Keys
        If key <> "index" Then
            row = row + 1
            Cells(row, col).Value = key
            Cells(row, col + 1).Value = data(key)(0)
            Cells(row, col + 2).Value = data(key)(1)
        End If
    Next key

    AlpGet_Actions_Wrapper = ticker & "-" & api_token
    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Actions(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Actions_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Actions = result
End Function
