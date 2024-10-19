
Function AlpGet_quarterly_balancesheet(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim rowIndex As Integer, columnIndex As Integer
    Dim key As Variant
    Dim dataArray() As Variant
    Dim headers As Collection

    ' Initialize the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Construct the URL
    url = "http://127.0.0.1:5000/quarterly_balancesheet?ticker=" & ticker & "&api_token=" & api_token

    ' Make the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the response
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Get the data from the JSON response
    Set headers = New Collection
    rowIndex = Application.ThisCell.row
    columnIndex = Application.ThisCell.Column

    ' Extract data and headers
    For Each key In json("data").keys
        headers.Add key
    Next key

    ' Set headers in the first row
    For Each key In headers
        Cells(rowIndex, columnIndex).Value = key
        columnIndex = columnIndex + 1
    Next key

    ' Write data starting from the second row
    ReDim dataArray(1 To UBound(json("data")(headers(1))) + 1, 1 To headers.Count)
    
    ' Loop over the JSON data and place values in the array
    For rowIndex = 1 To UBound(json("data")(headers(1))) + 1
        For columnIndex = 1 To headers.Count
            dataArray(rowIndex, columnIndex) = json("data")(headers(columnIndex))(rowIndex - 1)
        Next columnIndex
    Next rowIndex

    ' Output the data to the worksheet starting at the cell where the function is called
    Application.ThisCell.Offset(1, 0).Resize(UBound(dataArray, 1), UBound(dataArray, 2)).Value = dataArray
End Function


Make sure to include a reference to the JSON converter (`JsonConverter.bas`) in your VBA project, which you can find online, for handling JSON parsing in VBA.