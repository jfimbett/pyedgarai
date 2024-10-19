
Function AlpGet_sec_filings(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim jsonResponse As Object
    Dim dataArray As Variant
    Dim i As Integer, j As Integer
    Dim headers As String
    Dim dataObj As Object
    Dim baseRow As Long
    Dim baseCol As Long

    ' Create XMLHTTP Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Construct URL based on input parameters
    Dim url As String
    url = "http://127.0.0.1:5000/sec_filings?ticker=" & ticker & "&api_token=" & api_token
    
    ' Send GET request to the API
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.Send
    
    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    dataArray = jsonResponse("data")
    
    ' Determine the starting point of the table in Excel
    baseRow = Application.Caller.Row
    baseCol = Application.Caller.Column
    
    ' Extract headers
    headers = Array("date", "edgarUrl", "epochDate", "maxAge", "title", "type", "exhibits_8-K", "exhibits_EXCEL", "exhibits_EX-3.2")
    
    ' Write headers to the worksheet
    For j = 0 To UBound(headers)
        Cells(baseRow, baseCol + j).Value = headers(j)
    Next j
    
    ' Write data to the worksheet
    For i = LBound(dataArray) To UBound(dataArray)
        j = 0
        Cells(baseRow + 1 + i, baseCol + j).Value = dataArray(i)("date")
        Cells(baseRow + 1 + i, baseCol + j + 1).Value = dataArray(i)("edgarUrl")
        Cells(baseRow + 1 + i, baseCol + j + 2).Value = dataArray(i)("epochDate")
        Cells(baseRow + 1 + i, baseCol + j + 3).Value = dataArray(i)("maxAge")
        Cells(baseRow + 1 + i, baseCol + j + 4).Value = dataArray(i)("title")
        Cells(baseRow + 1 + i, baseCol + j + 5).Value = dataArray(i)("type")
        
        If Not IsEmpty(dataArray(i)("exhibits")) Then
            If dataArray(i)("exhibits")("8-K") <> Empty Then
                Cells(baseRow + 1 + i, baseCol + j + 6).Value = dataArray(i)("exhibits")("8-K")
            End If
            If dataArray(i)("exhibits")("EXCEL") <> Empty Then
                Cells(baseRow + 1 + i, baseCol + j + 7).Value = dataArray(i)("exhibits")("EXCEL")
            End If
            ' Additionally check for "EX-3.2" if exists
            If dataArray(i)("exhibits").Exists("EX-3.2") Then
                Cells(baseRow + 1 + i, baseCol + j + 8).Value = dataArray(i)("exhibits")("EX-3.2")
            End If
        End If
    Next i
    
    AlpGet_sec_filings = "Data Retrieved"

    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
End Function

Note: This code assumes that you have added or are using a JSON parsing library, such as "VBA-JSON" for handling JSON data in VBA. You should add the necessary library reference to your VBA project to use `JsonConverter.ParseJson`.