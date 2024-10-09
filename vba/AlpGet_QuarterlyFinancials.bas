
Function AlpGet_QuarterlyFinancials(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonData As Object
    Dim dict As Object
    Dim i As Integer
    Dim j As Integer
    
    ' Set the URL
    url = "http://127.0.0.1:5000/quarterly_financials?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get the JSON response
    jsonResponse = http.responseText
    
    ' Parse the JSON response
    Set jsonData = JsonConverter.ParseJson(jsonResponse)
    
    ' Check if JSON data is available and contains "data"
    If Not jsonData Is Nothing And Not jsonData("data") Is Nothing Then
        Set dict = jsonData("data")
        
        ' Write the table headers
        j = 0
        For Each key In dict
            ThisWorkbook.Sheets(1).Cells(1, j + 1).Value = key
            j = j + 1
        Next key
        
        ' Write the data
        i = 0
        For Each key In dict
            j = 1
            If IsArray(dict(key)) Then
                For Each value In dict(key)
                    If IsObject(value) Then
                        ThisWorkbook.Sheets(1).Cells(j + 1, i + 1).Value = "Object"
                    Else
                        ThisWorkbook.Sheets(1).Cells(j + 1, i + 1).Value = value
                    End If
                    j = j + 1
                Next value
            End If
            i = i + 1
        Next key
    End If
    
    Set jsonData = Nothing
    Set http = Nothing
End Function


**Note:** Before you can successfully use this code, you'll need to add a JSON parser to your VBA environment. One commonly used library is `JsonConverter`, which you can find on GitHub under VBA tools for JSON parsing (search for `VBA-JSON`). Include `JsonConverter` in your project to enable JSON parsing. Additionally, adjust the sheet reference `Sheets(1)` as needed.