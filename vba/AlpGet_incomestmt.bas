
Function AlpGet_incomestmt(ticker As String, api_token As String)

    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim jsonData As Object
    
    ' Create HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Set URL
    url = "http://127.0.0.1:5000/incomestmt?ticker=" & ticker & "&api_token=" & api_token
    
    ' Initialize HTTP request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Set jsonData = jsonResponse("data")
    
    ' Write to Excel
    Dim ws As Worksheet
    Set ws = Application.Caller.Worksheet
    
    Dim r As Long, c As Long
    r = Application.Caller.Row
    c = Application.Caller.Column
    
    Dim key As Variant
    Dim colIndex As Long
    colIndex = 0

    ' Write headers
    For Each key In jsonData.Keys
        ws.Cells(r, c + colIndex).Value = key
        colIndex = colIndex + 1
    Next key

    ' Find maximum number of rows
    Dim maxRows As Long
    maxRows = 0
    For Each key In jsonData.Keys
        If UBound(jsonData(key)) > maxRows Then
            maxRows = UBound(jsonData(key))
        End If
    Next key

    ' Write data
    Dim rowIndex As Long
    For rowIndex = 1 To maxRows + 1
        colIndex = 0
        For Each key In jsonData.Keys
            If rowIndex <= UBound(jsonData(key)) + 1 Then
                ws.Cells(r + rowIndex, c + colIndex).Value = jsonData(key)(rowIndex - 1)
            End If
            colIndex = colIndex + 1
        Next key
    Next rowIndex

    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
    Set jsonData = Nothing

End Function


**Note:** The code assumes that you have a JSON parsing library, such as `JsonConverter` (which you can find as a downloadable `.bas` file on various VBA-related websites), referenced into your VBA environment. Make sure to include that parsing library, as VBA does not include native JSON parsing.