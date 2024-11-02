
Function AlpGet_major_holders_Wrapper(ticker As String, api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/major_holders?ticker=" & ticker & "&api_token=" & api_token

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
    
    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers
    Cells(row, col).Value = "Breakdown"
    Cells(row, col + 1).Value = "Insiders Percent Held"
    Cells(row, col + 2).Value = "Institutions Percent Held"
    Cells(row, col + 3).Value = "Institutions Float Percent Held"
    Cells(row, col + 4).Value = "Institutions Count"

    row = row + 1
    Cells(row, col).Value = data("Breakdown")(1)
    Cells(row, col + 1).Value = data("insidersPercentHeld")(1)
    Cells(row, col + 2).Value = data("institutionsPercentHeld")(1)
    Cells(row, col + 3).Value = data("institutionsFloatPercentHeld")(1)
    Cells(row, col + 4).Value = data("institutionsCount")(1)

    AlpGet_major_holders_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_major_holders(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_major_holders_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_major_holders = result
End Function
