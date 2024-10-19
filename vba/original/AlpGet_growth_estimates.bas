
Function AlpGet_growth_estimates(ticker As String, api_token As String) As Variant
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/growth_estimates?ticker=" & ticker & "&api_token=" & api_token

    With http
        .Open "GET", url, False
        .setRequestHeader "accept", "application/json"
        .send
        Dim response As String
        response = .responseText
    End With

    Dim json As Object
    Set json = JsonConverter.ParseJson(response)
    
    Dim row As Long, col As Long
    Dim headers As Collection
    Dim data As Collection

    Set headers = json("data")("index")
    row = Application.Caller.Row
    col = Application.Caller.Column

    ' Write headers to the sheet
    Dim header As Variant
    For Each header In headers
        Cells(row, col).Value = header
        col = col + 1
    Next header

    ' Write data to the sheet
    Dim key As Variant
    For Each key In json("data").Keys
        col = Application.Caller.Column
        row = row + 1
        Cells(row, col).Value = key
        Set data = json("data")(key)
        Dim item As Variant
        For Each item In data
            col = col + 1
            If IsNull(item) Then
                Cells(row, col).Value = "NaN"
            Else
                Cells(row, col).Value = item
            End If
        Next item
    Next key
End Function


**Note**: You will need a JSON parser library in VBA, such as the "JsonConverter" library, to handle the JSON response. You can find the `JsonConverter.bas` module through open source repositories like GitHub. Add it to your VBA project before using this code.