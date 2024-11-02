
Function AlpGet_AllAccounts_Wrapper(api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim key As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/all_accounts?api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Write data starting next to the active cell
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Iterate over each key in the JSON response
    For Each key In jsonResponse.Keys
        ' Write the key name as header
        Cells(row, col).Value = key
        row = row + 1
        
        ' Get data for each account key
        Set data = jsonResponse(key)
        
        ' Write sub-keys and their values below each key
        Dim subkey As Variant
        For Each subkey In data.Keys
            Cells(row, col).Value = subkey
            Cells(row, col + 1).Value = data(subkey)
            row = row + 1
        Next subkey
    Next key

    AlpGet_AllAccounts_Wrapper = "All Accounts Data Retrieved"

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_AllAccounts(api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_AllAccounts_Wrapper(""" & api_token & """)")
    AlpGet_AllAccounts = result
End Function
