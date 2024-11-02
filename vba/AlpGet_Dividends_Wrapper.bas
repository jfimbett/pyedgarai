
Function AlpGet_Dividends_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim i As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/dividends?ticker=" & ticker & "&api_token=" & api_token

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

    Dim row As Long
    Dim col As Long
    row = ActiveCell.Row + 1
    col = ActiveCell.Column

    ' Write headers
    Cells(row, col).Value = "Date"
    Cells(row, col + 1).Value = "Dividends"
    
    ' Iterate over the 'Date' and 'Dividends' arrays in the 'data'
    For i = 1 To data("Date").Count
        row = row + 1
        Cells(row, col).Value = data("Date")(i)
        Cells(row, col + 1).Value = data("Dividends")(i)
    Next i

    AlpGet_Dividends_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Dividends(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Dividends_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_Dividends = result
End Function
