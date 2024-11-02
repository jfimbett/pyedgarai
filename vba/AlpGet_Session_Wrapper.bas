
Function AlpGet_Session_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant

    ' Set the endpoint URL
    url = "http://localhost:5000/session?ticker=" & ticker & "&api_token=" & api_token

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
    data = jsonResponse("data")
    
    ' Start writing data to the cell below the one where the function is called
    Dim row As Long
    Dim col As Long
    row = ActiveCell.Row + 1
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value = "data"
    
    ' Write the data below the headers
    row = row + 1
    Cells(row, col).Value = data
    
    AlpGet_Session_Wrapper = "Session Retrieved"

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Session(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Session_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Session = result
End Function
