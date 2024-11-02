
Function AlpGet_Institutional_Holders_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long
    
    ' Set the endpoint URL
    url = "http://localhost:5000/institutional_holders?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value = "Date Reported"
    Cells(row, col + 1).Value = "Holder"
    Cells(row, col + 2).Value = "pctHeld"
    Cells(row, col + 3).Value = "Shares"
    Cells(row, col + 4).Value = "Value"
    row = row + 1

    Dim i As Integer
    For i = 1 To data("Holder").Count
        Cells(row, col).Value = data("Date Reported")(i)
        Cells(row, col + 1).Value = data("Holder")(i)
        Cells(row, col + 2).Value = data("pctHeld")(i)
        Cells(row, col + 3).Value = data("Shares")(i)
        Cells(row, col + 4).Value = data("Value")(i)
        row = row + 1
    Next i

    AlpGet_Institutional_Holders_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Institutional_Holders(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Institutional_Holders_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Institutional_Holders = result
End Function
