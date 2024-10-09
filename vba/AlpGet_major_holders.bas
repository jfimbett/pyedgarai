
Function AlpGet_major_holders(ticker As String, api_token As String)
    Dim url As String
    Dim http As Object
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim headers As Object
    Dim r As Range
    Dim c As Long
    
    ' Construct the URL
    url = "http://127.0.0.1:5000/major_holders?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP request object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Send the GET request
    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
        response = .responseText
    End With
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(response)
    Set data = json("data")
    
    ' Writing data to the spreadsheet
    Set r = Application.Caller
    c = 0
    For Each headers In data
        r.Offset(0, c).Value = headers
        r.Offset(1, c).Value = data(headers)(1)
        c = c + 1
    Next headers
    
End Function

