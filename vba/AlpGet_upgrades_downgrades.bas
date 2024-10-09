
Function AlpGet_upgrades_downgrades(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonObject As Object
    Dim data As Object
    Dim index As Variant
    Dim i As Long, j As Long

    ' Initialize the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Define the API URL
    url = "http://127.0.0.1:5000/upgrades_downgrades?ticker=" & ticker & "&api_token=" & api_token
    
    ' Send the GET request
    With http
        .Open "GET", url, False
        .setRequestHeader "Accept", "application/json"
        .send
        jsonResponse = .responseText
    End With

    ' Parse the JSON response
    Set jsonObject = JsonConverter.ParseJson(jsonResponse)
    Set data = jsonObject("data")
    index = data("index")

    ' Write the headers to the worksheet
    For j = LBound(index) To UBound(index)
        ActiveCell.Offset(0, j).Value = index(j)
    Next j

    ' Write the data to the worksheet
    i = 1
    For Each entry In data.Keys
        If entry <> "index" Then
            For j = LBound(data(entry)) To UBound(data(entry))
                ActiveCell.Offset(i, j).Value = data(entry)(j)
            Next j
            i = i + 1
        End If
    Next entry
End Function

