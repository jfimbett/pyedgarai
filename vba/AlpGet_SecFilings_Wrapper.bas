
Function AlpGet_SecFilings_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/sec_filings?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value     = "date"
    Cells(row, col + 1).Value = "edgarUrl"
    Cells(row, col + 2).Value = "epochDate"
    Cells(row, col + 3).Value = "8-K Exhibit"
    Cells(row, col + 4).Value = "EXCEL Exhibit"
    Cells(row, col + 5).Value = "EX-3.2 Exhibit"
    Cells(row, col + 6).Value = "maxAge"
    Cells(row, col + 7).Value = "title"
    Cells(row, col + 8).Value = "type"
    
    ' Iterate over each item in the 'data' array and write to the sheet
    Dim item As Variant
    For Each item In data
        row = row + 1
        Cells(row, col).Value     = item("date")
        Cells(row, col + 1).Value = item("edgarUrl")
        Cells(row, col + 2).Value = item("epochDate")
        If item("exhibits").Exists("8-K") Then Cells(row, col + 3).Value = item("exhibits")("8-K")
        If item("exhibits").Exists("EXCEL") Then Cells(row, col + 4).Value = item("exhibits")("EXCEL")
        If item("exhibits").Exists("EX-3.2") Then Cells(row, col + 5).Value = item("exhibits")("EX-3.2")
        Cells(row, col + 6).Value = item("maxAge")
        Cells(row, col + 7).Value = item("title")
        Cells(row, col + 8).Value = item("type")
    Next item

    AlpGet_SecFilings_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_SecFilings(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_SecFilings_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_SecFilings = result
End Function
