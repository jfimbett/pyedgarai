
Function AlpGet_Comparables_Wrapper(cik As String, variables_to_compare As String, extra_variables As String, method As String, api_token As String, industry_digits As String, size_interval As String, profitability_interval As String, growth_rate_interval As String, capital_structure_interval As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim key As Variant
    Dim col As Long
    Dim rowOffset As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/comparables?cik=" & cik & "&" & variables_to_compare & "&" & extra_variables & "&method=" & method & "&api_token=" & api_token & "&industry_digits=" & industry_digits & "&size_interval=" & size_interval & "&profitability_interval=" & profitability_interval & "&growth_rate_interval=" & growth_rate_interval & "&capital_structure_interval=" & capital_structure_interval

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)
    If jsonResponse Is Nothing Then Exit Function  ' Check if response is valid JSON
    
    rowOffset = 0
    col = ActiveCell.Column
    
    ' Write headers
    For Each key In jsonResponse
        Cells(ActiveCell.Row + rowOffset, col).Value = key
        rowOffset = rowOffset + 1
    Next key
    
    ' Write values
    rowOffset = 0
    For Each key In jsonResponse
        Cells(ActiveCell.Row + rowOffset, col + 1).Value = jsonResponse(key)("0")
        rowOffset = rowOffset + 1
    Next key

    AlpGet_Comparables_Wrapper = "Completed"
    Exit Function
    
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " at line " & Erl
    Exit Function
End Function

Function AlpGet_Comparables(cik As String, variables_to_compare As String, extra_variables As String, method As String, api_token As String, industry_digits As String, size_interval As String, profitability_interval As String, growth_rate_interval As String, capital_structure_interval As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Comparables_Wrapper(" & """" & cik & """" & "," & """" & variables_to_compare & """" & "," & """" & extra_variables & """" & "," & """" & method & """" & "," & """" & api_token & """" & "," & """" & industry_digits & """" & "," & """" & size_interval & """" & "," & """" & profitability_interval & """" & "," & """" & growth_rate_interval & """" & "," & """" & capital_structure_interval & """" & ")")
    AlpGet_Comparables = result
End Function
