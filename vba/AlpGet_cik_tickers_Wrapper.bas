
Function AlpGet_cik_tickers_Wrapper(api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim key As Variant
    Dim values As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/cik_tickers?api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value = "CIK"
    Cells(row, col + 1).Value = "Ticker"

    ' Iterate over each key-value in the response and write to the sheet
    For Each key In jsonResponse.Keys
        row = row + 1
        Cells(row, col).Value = key
        Set values = jsonResponse(key)
        Cells(row, col + 1).Value = Join(Application.WorksheetFunction.Transpose(Application.Index(values, 0, 0)), ", ")
    Next key

    AlpGet_cik_tickers_Wrapper = "Request successful"

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_cik_tickers(api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_cik_tickers_Wrapper(""" & api_token & """)")
    AlpGet_cik_tickers = result
End Function
