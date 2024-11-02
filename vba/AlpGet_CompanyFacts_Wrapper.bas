
Function AlpGet_CompanyFacts_Wrapper(cik As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim entityFacts As Object
    Dim shares As Object
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/company_facts?cik=" & cik & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Get data from the response
    If jsonResponse.Exists("facts") Then
        Set shares = jsonResponse("facts")("dei")("EntityCommonStockSharesOutstanding")("units")("shares")
        
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

        ' Iterate over each item in the 'shares' array and write to the sheet
        Dim item As Variant
        For Each item In shares
            row = row + 1
            Cells(row, col).Value = item("accn")
            Cells(row, col + 1).Value = item("end")
            Cells(row, col + 2).Value = item("filed")
            Cells(row, col + 3).Value = item("form")
            Cells(row, col + 4).Value = item("fp")
            Cells(row, col + 5).Value = item("fy")
            Cells(row, col + 6).Value = item("val")
        Next item
    End If

    AlpGet_CompanyFacts_Wrapper = "cik-" & cik

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_CompanyFacts(cik As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_CompanyFacts_Wrapper(""" & cik & """, """ & api_token & """)")
    AlpGet_CompanyFacts = result
End Function
