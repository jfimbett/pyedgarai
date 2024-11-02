
Function AlpGet_upgrades_downgrades_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim keys As Variant
    Dim row As Long
    Dim col As Long
    Dim key As Variant

    ' Set the endpoint URL
    url = "http://localhost:5000/upgrades_downgrades?ticker=" & ticker & "&api_token=" & api_token

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
    
    row = ActiveCell.Row + 1
    col = ActiveCell.Column
    
    ' Write index as headers
    keys = data("index")
    For Each key In keys
        Cells(row, col).Value = key
        col = col + 1
    Next key
    
    ' Write data rows
    For Each key In data.Keys
        If key <> "index" Then
            col = ActiveCell.Column
            row = row + 1
            For Each item In data(key)
                Cells(row, col).Value = item
                col = col + 1
            Next item
        End If
    Next key

    AlpGet_upgrades_downgrades_Wrapper = ticker

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_upgrades_downgrades(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_upgrades_downgrades_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_upgrades_downgrades = result
End Function
