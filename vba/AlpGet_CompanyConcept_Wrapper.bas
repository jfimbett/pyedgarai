
Function AlpGet_CompanyConcept_Wrapper(cik As String, tag As String, taxonomy As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim units As Object
    Dim unit As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/company_concept?cik=" & cik & "&tag=" & tag & "&taxonomy=" & taxonomy & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'units' key exists in the response
    If Not jsonResponse.Exists("units") Then Exit Function

    ' Display jsonResponse
    Set units = jsonResponse("units")
    
    row = ActiveCell.Row + 1
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value     = "accn"
    Cells(row, col + 1).Value = "end"
    Cells(row, col + 2).Value = "filed"
    Cells(row, col + 3).Value = "form"
    Cells(row, col + 4).Value = "fp"
    Cells(row, col + 5).Value = "fy"
    Cells(row, col + 6).Value = "val"

    ' Since units is a dictionary with currency keys, iterate over its items
    For Each unit In units.Items
        Dim item As Variant
        For Each item In unit
            row = row + 1
            Cells(row, col).Value     = item("accn")
            Cells(row, col + 1).Value = item("end")
            Cells(row, col + 2).Value = item("filed")
            Cells(row, col + 3).Value = item("form")
            Cells(row, col + 4).Value = item("fp")
            Cells(row, col + 5).Value = item("fy")
            Cells(row, col + 6).Value = item("val")
        Next item
    Next unit

    AlpGet_CompanyConcept_Wrapper = cik & "-" & tag & "-" & taxonomy

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_CompanyConcept(cik As String, tag As String, taxonomy As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_CompanyConcept_Wrapper(" & """" & cik & """" & ", " & """" & tag & """" & ", " & """" & taxonomy & """" & ", " & """" & api_token & """" & ")")
    AlpGet_CompanyConcept = result
End Function
