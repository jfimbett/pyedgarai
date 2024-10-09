
Function AlpGet_earnings_dates(ticker As String, api_token As String)
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Construct the API endpoint URL
    Dim url As String
    url = "http://127.0.0.1:5000/earnings_dates?ticker=" & ticker & "&api_token=" & api_token

    ' Open the request
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.Send

    ' Process the response
    Dim jsonResponse As Object
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Dim data As Object
    Set data = jsonResponse("data")
    
    ' Write the response to the worksheet
    Dim startCell As Range
    Set startCell = Application.Caller
    Dim index As Variant
    Dim dateKey As Variant
    
    ' Write header row
    For Each index In data("index")
        startCell.Offset(0, 1).Value = index
        Set startCell = startCell.Offset(0, 1)
    Next index

    ' Write data rows
    Set startCell = Application.Caller
    For Each dateKey In data.Keys
        If dateKey <> "index" Then
            startCell.Value = dateKey
            Dim values As Variant
            values = data(dateKey)
            Dim i As Integer
            For i = LBound(values) To UBound(values)
                startCell.Offset(0, i + 1).Value = values(i)
            Next i
            Set startCell = startCell.Offset(1, 0)
        End If
    Next dateKey
End Function


This function assumes that a JSON parsing library like `VBA-JSON` is available in your VBA environment (`JsonConverter.bas` should be imported into your VBA project for `JsonConverter.ParseJson`). Adjust references and imports as necessary for your environment.