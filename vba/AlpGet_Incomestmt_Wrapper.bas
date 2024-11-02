
Function AlpGet_Incomestmt_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long
    Dim key As Variant
    Dim i As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/incomestmt?ticker=" & ticker & "&api_token=" & api_token

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
    i = 0
    For Each key In data.Keys
        Cells(row, col + i).Value = key
        i = i + 1
    Next key

    ' Write data
    For i = 1 To UBound(data("index"))
        row = row + 1
        For Each key In data.Keys
            Cells(row, col).Value = data(key)(i - 1)
            col = col + 1
        Next key
        col = ActiveCell.Column
    Next i

    AlpGet_Incomestmt_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Incomestmt(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Incomestmt_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Incomestmt = result
End Function
