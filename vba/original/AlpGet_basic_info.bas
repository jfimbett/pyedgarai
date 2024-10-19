
Function AlpGet_basic_info(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/basic_info?ticker=" & ticker & "&api_token=" & api_token

    ' Make the HTTP request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    Dim jsonResponse As String
    jsonResponse = http.responseText
    
    ' Parse JSON response using VBA-JSON library
    Dim json As Object
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    Dim keys As Variant
    Dim rowCount As Long
    Dim key As Variant
    
    ' Start position to write response data
    Dim startRow As Long, startCol As Long
    startRow = Application.Caller.Row
    startCol = Application.Caller.Column
    
    ' Check if the data is a dictionary
    If json.Exists("data") Then
        keys = json("data").keys
        
        rowCount = 0
        For Each key In keys
            Cells(startRow + rowCount, startCol).Value = key
            Cells(startRow + rowCount, startCol + 1).Value = json("data")(key)
            rowCount = rowCount + 1
        Next key
    Else
        ' Simple fallback to write whole JSON response
        Cells(startRow, startCol).Value = jsonResponse
    End If
    
    ' Set the function to return the top-left cell of the table
    AlpGet_basic_info = Cells(startRow, startCol).Value
End Function


Note: To run this code, you'll need to include a JSON parser library for VBA such as `VBA-JSON`.