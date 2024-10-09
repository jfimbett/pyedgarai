
Function AlpGet_cik_sic(api_token As String, endpoint As String) As Variant
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim jsonResponse As Object
    Dim row As Integer
    Dim col As Integer
    Dim key As Variant

    ' Create the URL
    url = endpoint & "?api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")

    ' Initialize the HTTP request
    On Error GoTo ErrorHandler
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Get the response
    response = http.responseText

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(response)
    
    ' Determine the start position for table output
    row = Application.Caller.Row
    col = Application.Caller.Column

    ' Write the JSON keys and values to cells
    For Each key In jsonResponse
        Cells(row, col).Value = key
        Cells(row, col + 1).Value = jsonResponse(key)
        row = row + 1
    Next key

    Exit Function

ErrorHandler:
    MsgBox "Error in API call: " & Err.Description
End Function


To use the above function, you will need a JSON parser library for VBA, such as the `JsonConverter` module. You can find and import this module from its repository on GitHub to handle JSON parsing:

1. JSON converter module: https://github.com/VBA-tools/VBA-JSON

Import the JsonConverter module into your VBA project to enable JSON parsing.