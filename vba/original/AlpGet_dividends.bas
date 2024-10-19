
Function AlpGet_dividends(ticker As String, api_token As String)
    Dim url As String
    Dim xhr As Object
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim i As Long
    Dim startCell As Range

    ' Construct the URL
    url = "http://127.0.0.1:5000/dividends?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHttpRequest object
    Set xhr = CreateObject("MSXML2.ServerXMLHTTP.6.0")

    ' Make the HTTP GET request
    xhr.Open "GET", url, False
    xhr.setRequestHeader "accept", "application/json"
    xhr.send

    ' Get the response
    response = xhr.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(response)
    Set data = json("data")

    ' Get the starting cell where the function is called
    Set startCell = Application.Caller

    ' Write the headers
    startCell.Offset(0, 0).Value = "Date"
    startCell.Offset(0, 1).Value = "Dividends"

    ' Write the data to the cells
    For i = 1 To data("Date").Count
        startCell.Offset(i, 0).Value = data("Date")(i)
        startCell.Offset(i, 1).Value = data("Dividends")(i)
    Next i
End Function


Make sure you have a JSON parser for VBA, such as the "JsonConverter" module from VBA-JSON, for the `JsonConverter.ParseJson` function to work. You can download it from GitHub and include it in your VBA project.