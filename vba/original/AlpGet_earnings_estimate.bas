
Function AlpGet_earnings_estimate(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    Dim url As String
    url = "http://127.0.0.1:5000/earnings_estimate?ticker=" & ticker & "&api_token=" & api_token

    ' Making the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parsing JSON response
    Dim jsonResponse As Object
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)

    ' Writing response to Excel cell
    Dim ws As Worksheet
    Set ws = Application.Caller.Worksheet
    Dim startCell As Range
    Set startCell = Application.Caller

    Dim data As Object
    Set data = jsonResponse("data")

    Dim index As Variant
    Dim keys As Variant
    Dim i As Long, j As Long

    index = data("index")
    keys = data.keys

    ' Write column headers
    For i = LBound(index) To UBound(index)
        ws.Cells(startCell.Row, startCell.Column + i).Value = index(i)
    Next i

    ' Write data to table
    j = 1
    For Each key In keys
        If key <> "index" Then
            ws.Cells(startCell.Row + j, startCell.Column).Value = key
            For i = LBound(data(key)) To UBound(data(key))
                ws.Cells(startCell.Row + j, startCell.Column + i + 1).Value = data(key)(i)
            Next i
            j = j + 1
        End If
    Next key
    
    AlpGet_earnings_estimate = "Data Imported"
End Function


Please make sure you have added the "JsonConverter.bas" module to your VBA project, which you can find on GitHub here: [VBA-JSON](https://github.com/VBA-tools/VBA-JSON). This module is necessary for parsing the JSON response. Additionally, you might need to handle any runtime errors that could arise from network issues or JSON parsing errors.