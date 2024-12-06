
Function AlpGet_Comparables_Wrapper(cik As String, method As String, api_token As String, industry_digits As String, size_interval As String, profitability_interval As String, growth_rate_interval As String, capital_structure_interval As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim key As Variant
    Dim subkey As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/comparables?cik=" & cik & "&method=" & method & "&api_token=" & api_token & "&industry_digits=" & industry_digits & "&size_interval=" & size_interval & "&profitability_interval=" & profitability_interval & "&growth_rate_interval=" & growth_rate_interval & "&capital_structure_interval=" & capital_structure_interval

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
    Dim headers As Collection
    Set headers = New Collection
    For Each key In jsonResponse
        headers.Add key
    Next key

    ' Write headers to the worksheet
    For col = 1 To headers.Count
        Cells(row, col).Value = headers(col - 1)
    Next col

    ' Iterate over each dictionary in the response and write to the sheet
    Dim maxIndex As Integer
    maxIndex = 0
    For Each key In jsonResponse
        If jsonResponse(key).Count > maxIndex Then maxIndex = jsonResponse(key).Count
    Next key
    
    Dim i As Integer
    For i = 0 To maxIndex - 1
        row = row + 1
        col = ActiveCell.Column
        For Each key In jsonResponse
            If jsonResponse(key).Exists(CStr(i)) Then
                Cells(row, col).Value = jsonResponse(key)(CStr(i))
            End If
            col = col + 1
        Next key
    Next i

    AlpGet_Comparables_Wrapper = cik & "-" & method & "-" & api_token

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Comparables(cik As String, method As String, api_token As String, industry_digits As String, size_interval As String, profitability_interval As String, growth_rate_interval As String, capital_structure_interval As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Comparables_Wrapper(" & Chr(34) & cik & Chr(34) & ", " & Chr(34) & method & Chr(34) & ", " & Chr(34) & api_token & Chr(34) & ", " & Chr(34) & industry_digits & Chr(34) & ", " & Chr(34) & size_interval & Chr(34) & ", " & Chr(34) & profitability_interval & Chr(34) & ", " & Chr(34) & growth_rate_interval & Chr(34) & ", " & Chr(34) & capital_structure_interval & Chr(34) & ")")
    AlpGet_Comparables = result
End Function
