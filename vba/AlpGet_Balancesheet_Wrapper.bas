
Function AlpGet_Balancesheet_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim headers As Collection
    Dim indexValues As Variant
    Dim header As Variant
    Dim i As Long, j As Long
    Dim row As Long, col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/balancesheet?ticker=" & ticker & "&api_token=" & api_token

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

    ' Set data object
    Set data = jsonResponse("data")
    
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Prepare headers from the dictionary keys
    Set headers = New Collection
    For Each key In data.Keys
        If key <> "index" Then headers.Add key
    Next key

    ' Write headers to the sheet
    Cells(row, col).Value = "Date"
    For j = 1 To headers.Count
        Cells(row, col + j).Value = headers(j)
    Next j
    
    ' Iterate over the 'index' and fill out data
    indexValues = data("index")
    For i = LBound(indexValues) To UBound(indexValues)
        row = row + 1
        Cells(row, col).Value = indexValues(i)
        For j = 1 To headers.Count
            header = headers(j)
            Cells(row, col + j).Value = data(header)(i)
        Next j
    Next i

    AlpGet_Balancesheet_Wrapper = ticker & "-" & api_token

Exit Function

ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Balancesheet(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Balancesheet_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Balancesheet = result
End Function
