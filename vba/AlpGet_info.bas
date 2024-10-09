
Function AlpGet_info(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    Dim url As String
    url = "http://127.0.0.1:5000/info?ticker=" & ticker & "&api_token=" & api_token

    ' Open the request
    http.Open "GET", url, False
    
    ' Set request headers
    http.setRequestHeader "accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Check for successful response
    If http.Status = 200 Then
        Dim jsonResponse As String
        jsonResponse = http.responseText
        
        ' Parse JSON response (requires reference to Microsoft Scripting Runtime)
        Dim jsonParser As Object
        Set jsonParser = JsonConverter.ParseJson(jsonResponse)
        
        Dim dataObj As Object
        Set dataObj = jsonParser("data")
        
        ' Determine the first cell of output
        Dim ws As Worksheet
        Set ws = Application.Caller.Worksheet
        
        Dim startRow As Long
        Dim startCol As Long
        startRow = Application.Caller.Row
        startCol = Application.Caller.Column
        
        Dim i As Long
        i = startRow

        Dim key As Variant
        For Each key In dataObj.Keys
            If TypeName(dataObj(key)) = "Collection" Then
                ' Handle list of dictionaries (array of objects)
                Dim j As Long
                j = 0
                Dim item As Object
                For Each item In dataObj(key)
                    Dim subKey As Variant
                    Dim col As Long
                    col = startCol
                    For Each subKey In item.Keys
                        ws.Cells(i + j, col).Value = subKey
                        ws.Cells(i + j + 1, col).Value = item(subKey)
                        col = col + 1
                    Next subKey
                    j = j + 2 ' double increment to separate sets
                Next item
            Else
                ' Handle simple key-value pairs
                ws.Cells(i, startCol).Value = key
                ws.Cells(i, startCol + 1).Value = dataObj(key)
                i = i + 1
            End If
        Next key
        
        AlpGet_info = "Data written successfully."
    Else
        AlpGet_info = "Error: " & http.Status & " " & http.statusText
    End If
    
    Set http = Nothing
End Function
