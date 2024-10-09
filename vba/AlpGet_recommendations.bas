
Function AlpGet_recommendations(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim jsonResponse As Object
    Dim baseUrl As String
    Dim url As String
    Dim ws As Worksheet
    Dim cell As Range
    Dim jsonData As Object
    Dim i As Long
    Dim key As Variant
    Dim headerRow As Range
    Dim firstCell As Range

    ' Set the worksheet and initial cell
    Set ws = Application.Caller.Worksheet
    Set cell = Application.Caller
    Set firstCell = cell

    ' Initialize HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    
    ' Create the URL for the API request
    baseUrl = "http://127.0.0.1:5000/recommendations"
    url = baseUrl & "?ticker=" & ticker & "&api_token=" & api_token
    
    ' Make the request to the API
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Set jsonData = jsonResponse("data")

    ' Write headers
    For Each key In jsonData.Keys
        cell.Value = key
        Set cell = cell.Offset(0, 1)
    Next key
    
    ' Write data
    Set headerRow = ws.Range(firstCell, cell.Offset(-1, -1))
    For i = 1 To jsonData("period").Count
        Set cell = firstCell.Offset(i, 0)
        For Each key In jsonData.Keys
            cell.Value = jsonData(key)(i - 1)
            Set cell = cell.Offset(0, 1)
        Next key
    Next i

    Set AlpGet_recommendations = headerRow
End Function


Note: To use the JSON parsing function `JsonConverter.ParseJson`, you need to include a JSON library in your VBA project. A common choice is to use "JsonConverter" which you can download from this [GitHub repository](https://github.com/VBA-tools/VBA-JSON) and add to your VBA project.