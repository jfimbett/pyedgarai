
Function AlpGet_CleanName_Wrapper(name As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/clean_name?name=" & name & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Write the response to the sheet
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    If jsonResponse.Exists("clean_name") Then
        Cells(row, col).Value = jsonResponse("clean_name")
    End If

    AlpGet_CleanName_Wrapper = name & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_CleanName(name As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_CleanName_Wrapper(""" & name & """, """ & api_token & """)")
    AlpGet_CleanName = result
End Function
