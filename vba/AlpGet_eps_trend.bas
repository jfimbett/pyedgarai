
Function AlpGet_eps_trend(ticker As String, api_token As String)

    Dim http As Object
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    Dim url As String
    url = "http://127.0.0.1:5000/eps_trend?ticker=" & ticker & "&api_token=" & api_token
    
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim response As String
    response = http.responseText

    Dim json As Object
    Set json = JsonConverter.ParseJson(response)
    
    Dim rowIndex As Integer
    Dim colIndex As Integer
    Dim key As Variant
    Dim arrIndex As Variant
    Dim cell As Range
    Set cell = Application.Caller
    
    ' Output table headers
    colIndex = 0
    For Each key In json("data")
        cell.Offset(0, colIndex).Value = key
        colIndex = colIndex + 1
    Next key
    
    ' Output table data
    rowIndex = 1
    For arrIndex = 0 To UBound(json("data")("index"))
        colIndex = 0
        For Each key In json("data")
            cell.Offset(rowIndex, colIndex).Value = json("data")(key)(arrIndex)
            colIndex = colIndex + 1
        Next key
        rowIndex = rowIndex + 1
    Next arrIndex
    
End Function


**Note**: This code uses `JsonConverter`, a popular VBA JSON library. Ensure you have included this library in your VBA project for JSON parsing. It can be found at: https://github.com/VBA-tools/VBA-JSON