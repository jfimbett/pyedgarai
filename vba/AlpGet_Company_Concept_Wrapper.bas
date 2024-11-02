
Function AlpGet_Company_Concept_Wrapper(cik As String, tag As String, taxonomy As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim unitsData As Variant
    Dim item As Variant
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

    ' Check if 'units' key exists and has data in the response
    If Not jsonResponse.Exists("units") Then Exit Function

    ' Display units data
    If jsonResponse("units").Exists("USD") Then
        Set unitsData = jsonResponse("units")("USD")
    Else
        Exit Function
    End If

    row = ActiveCell.Row + 1
    col = ActiveCell.Column

    ' Write headers
    Cells(row, col).Value = "accn"
    Cells(row, col + 1).Value = "end"
    Cells(row, col + 2).Value = "filed"
    Cells(row, col + 3).Value = "form"
    Cells(row, col + 4).Value = "fp"
    Cells(row, col + 5).Value = "fy"
    Cells(row, col + 6).Value = "val"

    ' Iterate over each item in the 'unitsData' array and write to the sheet
    For Each item In unitsData
        row = row + 1
        Cells(row, col).Value = item("accn")
        Cells(row, col + 1).Value = item("end")
        Cells(row, col + 2).Value = item("filed")
        Cells(row, col + 3).Value = item("form")
        Cells(row, col + 4).Value = item("fp")
        Cells(row, col + 5).Value = item("fy")
        Cells(row, col + 6).Value = item("val")
    Next item

    AlpGet_Company_Concept_Wrapper = cik & "-" & tag & "-" & taxonomy

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Company_Concept(cik As String, tag As String, taxonomy As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Company_Concept_Wrapper(""" & cik & """, """ & tag & """, """ & taxonomy & """, """ & api_token & """)")
    AlpGet_Company_Concept = result
End Function
