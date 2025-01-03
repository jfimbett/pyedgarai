
Function AlpGet_Proxy_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object

    ' Set the endpoint URL
    url = "http://localhost:5000/proxy?ticker=" & ticker & "&api_token=" & api_token

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

    ' Write response to the cell where the UDF is called
    Cells(ActiveCell.Row, ActiveCell.Column).Value = jsonResponse("data")

    AlpGet_Proxy_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Proxy(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Proxy_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Proxy = result
End Function