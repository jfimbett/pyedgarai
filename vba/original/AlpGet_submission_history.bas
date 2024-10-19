
Function AlpGet_submission_history(cik As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    
    Dim endpoint As String
    endpoint = "http://127.0.0.1:5000/submission_history?cik=" & cik & "&api_token=" & api_token
    
    http.Open "GET", endpoint, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim jsonResponse As String
    jsonResponse = http.responseText
    
    ' Parse JSON response
    Dim json As Object
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Get the starting cell
    Dim startCell As Range
    Set startCell = Application.Caller
    
    ' Handle the response as a dictionary
    Dim row As Integer
    Dim col As Integer
    row = 0
    col = 0
    
    Dim key As Variant
    For Each key In json.Keys
        startCell.Offset(row, col).Value = key
        row = row + 1
        
        If TypeName(json(key)) = "Collection" Then
            Dim subKey As Variant
            Dim subDict As Object
            Set subDict = json(key)
            
            For Each subKey In subDict.Keys
                col = col + 1
                startCell.Offset(row, col).Value = subKey
                startCell.Offset(row + 1, col).Value = subDict(subKey)
            Next
            
            row = row + 2
            col = 0
        Else
            startCell.Offset(row, col).Value = json(key)
        End If
    Next key
    
    Set http = Nothing
    Set json = Nothing
End Function


Note: Make sure you have included a reference to "Microsoft Scripting Runtime" and have a JSON parser module like "JsonConverter" available in your VBA project (e.g. by using the JSON VBA library from GitHub).