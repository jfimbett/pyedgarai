
Function AlpGet_SubmissionHistory_Wrapper(cik As String, api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim addresses As Object
    Dim filings As Object
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/submission_history?cik=" & cik & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Start writing data to the sheet
    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers for address
    Cells(row, col).Value = "Type"
    Cells(row, col + 1).Value = "City"
    Cells(row, col + 2).Value = "StateOrCountry"
    Cells(row, col + 3).Value = "Street1"
    Cells(row, col + 4).Value = "Street2"
    Cells(row, col + 5).Value = "ZipCode"
    row = row + 1

    ' Iterate over each type of address and write to the sheet
    For Each addresses In jsonResponse("addresses")
        Cells(row, col).Value = "Business"
        Cells(row, col + 1).Value = addresses("business")("city")
        Cells(row, col + 2).Value = addresses("business")("stateOrCountry")
        Cells(row, col + 3).Value = addresses("business")("street1")
        Cells(row, col + 4).Value = IIf(IsNull(addresses("business")("street2")), "", addresses("business")("street2"))
        Cells(row, col + 5).Value = addresses("business")("zipCode")
        
        row = row + 1
        Cells(row, col).Value = "Mailing"
        Cells(row, col + 1).Value = addresses("mailing")("city")
        Cells(row, col + 2).Value = addresses("mailing")("stateOrCountry")
        Cells(row, col + 3).Value = addresses("mailing")("street1")
        Cells(row, col + 4).Value = IIf(IsNull(addresses("mailing")("street2")), "", addresses("mailing")("street2"))
        Cells(row, col + 5).Value = addresses("mailing")("zipCode")

        row = row + 1
    Next addresses

    ' Write headers for filings
    row = row + 1 ' Leave a blank row between sections
    Cells(row, col).Value = "Filing Count"
    Cells(row, col + 1).Value = "Filing From"
    Cells(row, col + 2).Value = "Filing To"
    Cells(row, col + 3).Value = "Name"
    row = row + 1

    ' Iterate over each filing and write to the sheet
    For Each filings In jsonResponse("filings")("files")
        Cells(row, col).Value = filings("filingCount")
        Cells(row, col + 1).Value = filings("filingFrom")
        Cells(row, col + 2).Value = filings("filingTo")
        Cells(row, col + 3).Value = filings("name")
        row = row + 1
    Next filings

    AlpGet_SubmissionHistory_Wrapper = cik & "-" & api_token

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_SubmissionHistory(cik As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_SubmissionHistory_Wrapper(""" & cik & """, """ & api_token & """)")
    AlpGet_SubmissionHistory = result
End Function
