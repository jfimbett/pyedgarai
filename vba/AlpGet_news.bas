
Function AlpGet_news(ticker As String, api_token As String) As String
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim item As Object
    Dim i As Integer
    Dim cell As Range
    
    ' Get the current cell location
    Set cell = Application.Caller

    ' Create the URL with passed arguments
    url = "http://127.0.0.1:5000/news?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the JSON response
    jsonResponse = http.responseText
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Accessing the data array from the JSON
    Set data = json("data")
    
    ' Initialize column headers
    cell.Offset(0, 0).Value = "Title"
    cell.Offset(0, 1).Value = "Publisher"
    cell.Offset(0, 2).Value = "Link"
    cell.Offset(0, 3).Value = "Type"
    
    ' Looping through the items and filling in the Excel cells
    i = 1
    For Each item In data
        cell.Offset(i, 0).Value = item("title")
        cell.Offset(i, 1).Value = item("publisher")
        cell.Offset(i, 2).Value = item("link")
        cell.Offset(i, 3).Value = item("type")
        i = i + 1
    Next item
End Function


**Notes:**

- The code uses an external JSON parser (like "JsonConverter.bas"), which needs to be imported into your VBA project for parsing JSON.
- You can obtain "JsonConverter.bas" from reputable sources like GitHub.
- This function assumes that the JSON response has the same structure as shown. Adjust the fields accordingly if the JSON structure changes.