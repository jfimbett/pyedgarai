
Function AlpGet_Endpoint_Wrapper(var1 As String, var2 As String, token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim key As Variant
    Dim value As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://127.0.0.1:5000/endpoint?var1=" & var1 & "&var2=" & var2 & "&token=" & token

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

    ' Iterate over each key-value pair in the response and write to the sheet
    For Each key In jsonResponse.Keys
        value = jsonResponse(key)
        Cells(row, col).Value = key
        Cells(row, col + 1).Value = value
        row = row + 1
    Next key

    AlpGet_Endpoint_Wrapper = var1 & "-" & var2 & "-" & token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Endpoint(var1 As String, var2 As String, token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Endpoint_Wrapper(""" & var1 & """, """ & var2 & """, """ & token & """)")
    AlpGet_Endpoint = result
End Function
