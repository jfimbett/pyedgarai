
Function AlpGet_AnalystPriceTargets_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/analyst_price_targets?ticker=" & ticker & "&api_token=" & api_token

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

    row = ActiveCell.Row + 1
    col = ActiveCell.Column

    ' Write headers
    Cells(row, col).Value = "current"
    Cells(row, col + 1).Value = "high"
    Cells(row, col + 2).Value = "low"
    Cells(row, col + 3).Value = "mean"
    Cells(row, col + 4).Value = "median"

    ' Write data to the sheet
    Cells(row + 1, col).Value = data("current")
    Cells(row + 1, col + 1).Value = data("high")
    Cells(row + 1, col + 2).Value = data("low")
    Cells(row + 1, col + 3).Value = data("mean")
    Cells(row + 1, col + 4).Value = data("median")

    AlpGet_AnalystPriceTargets_Wrapper = ticker & "-" & api_token

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_AnalystPriceTargets(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_AnalystPriceTargets_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_AnalystPriceTargets = result
End Function
