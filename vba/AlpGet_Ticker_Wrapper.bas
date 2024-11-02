
Function AlpGet_Ticker_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object

    ' Set the endpoint URL
    url = "http://localhost:5000/ticker?ticker=" & ticker & "&api_token=" & api_token

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

    ' Write the 'data' value to the cell
    Cells(ActiveCell.Row, ActiveCell.Column).Value = jsonResponse("data")

    AlpGet_Ticker_Wrapper = ticker 

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_Ticker(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Ticker_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_Ticker = result
End Function
