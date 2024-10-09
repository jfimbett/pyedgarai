
Function AlpGet_cik_names(api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim key As Variant
    Dim rng As Range
    Dim columnIndex As Integer

    ' Initialize the URL
    url = "http://127.0.0.1:5000/cik_names?api_token=" & api_token

    ' Create the WinHttpRequest object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.Open "GET", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "accept", "application/json"

    ' Send the request
    http.send

    ' Get the response
    jsonResponse = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Determine the starting cell (where the function is called)
    Set rng = Application.Caller

    ' Check if the response is a dictionary
    If VBA.TypeName(json) = "Dictionary" Then
        ' Write JSON keys and values to the table starting from the call cell
        rng.Cells(1, 1).Value = "CIK"
        rng.Cells(1, 2).Value = "Name"
        rowIndex = 2
        For Each key In json.Keys
            rng.Cells(rowIndex, 1).Value = key
            rng.Cells(rowIndex, 2).Value = json(key)
            rowIndex = rowIndex + 1
        Next key
    Else
        rng.Value = "Invalid response format"
    End If

    ' Clean up
    Set http = Nothing
    Set json = Nothing
End Function


Note: This code assumes that you have a JSON parser set up in your VBA environment. If you don't have one, you'll need to include a JSON conversion library such as "VBA-JSON" by Tim Hall (https://github.com/VBA-tools/VBA-JSON) to parse the JSON data.