
Function AlpGet_EarningsEstimate_Wrapper(ticker As String, api_token As String) As String
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
    url = "http://localhost:5000/earnings_estimate?ticker=" & ticker & "&api_token=" & api_token

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
    For Each key In data("index")
        Cells(row, col).Value = key
        col = col + 1
    Next key
    
    row = row + 1
    
    ' Write data for each period
    Dim period As Variant
    For Each period In data.Keys
        If period <> "index" Then
            col = ActiveCell.Column
            For Each key In data("index")
                Cells(row, col).Value = data(period)(Application.Match(key, data("index"), 0) - 1)
                col = col + 1
            Next key
            row = row + 1
        End If
    Next period

    AlpGet_EarningsEstimate_Wrapper = ticker

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_EarningsEstimate(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_EarningsEstimate_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_EarningsEstimate = result
End Function
