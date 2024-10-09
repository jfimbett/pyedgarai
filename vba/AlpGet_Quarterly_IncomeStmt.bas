
Function AlpGet_Quarterly_IncomeStmt(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim i As Long, j As Long
    Dim headers As Collection
    Dim header As Variant

    ' Create the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/quarterly_incomestmt?ticker=" & ticker & "&api_token=" & api_token
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse the JSON response
    jsonResponse = http.responseText
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Extract data from JSON
    Set data = json("data")

    ' Set headers for the table
    Set headers = New Collection
    For Each header In data
        headers.Add header
    Next header

    ' Write headers to Excel
    For j = 1 To headers.Count
        ActiveCell.Offset(0, j - 1).Value = headers(j)
    Next j

    ' Determine the number of data rows
    Dim numRows As Long
    numRows = data(headers(1)).Count

    ' Write data to Excel
    For i = 1 To numRows
        For j = 1 To headers.Count
            If Not IsNull(data(headers(j))(i)) Then
                ActiveCell.Offset(i, j - 1).Value = data(headers(j))(i)
            Else
                ActiveCell.Offset(i, j - 1).Value = "NaN"
            End If
        Next j
    Next i
End Function


### Note

- The code uses a JSON parser (`JsonConverter.ParseJson`) available in VBA, which requires adding a JSON parsing library. You can download and add the `JsonConverter.bas` to your VBA project to enable JSON parsing.
- To add the JSON parser, you should download it from a trusted source such as [VBA-JSON](https://github.com/VBA-tools/VBA-JSON) and import it into your VBA project.
- Change the `ActiveCell` reference as needed depending on where you want the data to be written in your Excel sheet.