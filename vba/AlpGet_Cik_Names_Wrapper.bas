
Function AlpGet_Cik_Names_Wrapper(api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim key As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/cik_names?api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Start the table row and column
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value = "CIK"
    Cells(row, col + 1).Value = "Name"

    ' Iterate over each item in the jsonResponse and write to the sheet
    For Each key In jsonResponse.keys
        row = row + 1
        Cells(row, col).Value = key
        Cells(row, col + 1).Value = jsonResponse(key)
    Next key

    AlpGet_Cik_Names_Wrapper = api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Cik_Names(api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Cik_Names_Wrapper(""" & api_token & """)")
    AlpGet_Cik_Names = result
End Function
