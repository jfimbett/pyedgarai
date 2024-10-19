
Function AlpGet_balance_sheet(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim cell As Range
    Dim headers As Collection
    Dim rowIndex As Long
    Dim columnIndex As Long

    ' Set the API URL with parameters
    url = "http://127.0.0.1:5000/balance_sheet?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the JSON response
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Navigate to the data part of the JSON
    Set data = json("data")

    ' Get the starting cell
    Set cell = Application.Caller

    ' Create headers
    Set headers = New Collection
    For Each key In data.Keys
        If key <> "index" Then
            headers.Add key
        End If
    Next key

    ' Write headers to the first row
    columnIndex = 1
    For Each header In headers
        cell.Offset(0, columnIndex).Value = header
        columnIndex = columnIndex + 1
    Next header

    ' Write data to the cells below the header
    For rowIndex = 0 To UBound(data("index"))
        cell.Offset(rowIndex + 1, 0).Value = data("index")(rowIndex)
        columnIndex = 1
        For Each header In headers
            cell.Offset(rowIndex + 1, columnIndex).Value = data(header)(rowIndex)
            columnIndex = columnIndex + 1
        Next header
    Next rowIndex

    ' Return the result
    AlpGet_balance_sheet = "Data written starting from cell " & cell.Address

End Function
