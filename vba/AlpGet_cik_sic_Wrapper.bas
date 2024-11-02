
Function AlpGet_cik_sic_Wrapper(api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim key As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/cik_sic?api_token=" & api_token

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
    Cells(row, col + 1).Value = "SIC"

    ' Move to the next row
    row = row + 1

    ' Iterate over each key in the JSON response and write to the sheet
    For Each key In jsonResponse.Keys
        Cells(row, col).Value = key
        Cells(row, col + 1).Value = jsonResponse(key)
        row = row + 1
    Next key

    AlpGet_cik_sic_Wrapper = "Completed"

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_cik_sic(api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_cik_sic_Wrapper(""" & api_token & """)")
    AlpGet_cik_sic = result
End Function
