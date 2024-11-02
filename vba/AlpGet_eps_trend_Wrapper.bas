
Function AlpGet_eps_trend_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Dictionary
    Dim key As Variant
    Dim col As Long
    Dim rowOffset As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/eps_trend?ticker=" & ticker & "&api_token=" & api_token

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

    ' Write headers
    col = ActiveCell.Column
    rowOffset = 1
    Cells(ActiveCell.Row + rowOffset, col).Value = "index"
    rowOffset = rowOffset + 1

    ' Write index data
    For Each key In data.Keys
        Cells(ActiveCell.Row, col).Value = key
        rowOffset = 1
        For Each item In data(key)
            Cells(ActiveCell.Row + rowOffset, col).Value = item
            rowOffset = rowOffset + 1
        Next item
        col = col + 1
    Next key

    AlpGet_eps_trend_Wrapper = ticker & "-eps_trend"

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_eps_trend(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_eps_trend_Wrapper(" & Chr(34) & ticker & Chr(34) & ", " & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_eps_trend = result
End Function
