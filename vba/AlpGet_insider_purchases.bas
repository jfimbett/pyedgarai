
Function AlpGet_insider_purchases(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As String
    Dim json As Object
    Dim cell As Range
    Dim i As Integer
    Dim j As Integer
    
    url = "http://127.0.0.1:5000/insider_purchases?ticker=" & ticker & "&api_token=" & api_token

    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"
    xmlhttp.send

    jsonResponse = xmlhttp.responseText
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    Set cell = Application.Caller

    ' Determine if response is a dictionary with keys or list of dictionaries
    Dim dataKeys As Object
    Set dataKeys = json("data").keys

    ' Write keys to the top row of the table
    For i = 1 To dataKeys.Count
        cell.Offset(0, i - 1).Value = dataKeys(i - 1)
    Next i

    ' Write data values to the table
    Dim maxCount As Integer
    maxCount = 0
    For Each key In dataKeys
        maxCount = WorksheetFunction.Max(maxCount, UBound(json("data")(key)))
    Next key
    
    For i = 1 To maxCount
        For j = 1 To dataKeys.Count
            cell.Offset(i, j - 1).Value = json("data")(dataKeys(j - 1))(i - 1)
        Next j
    Next i
   
    ' Return nothing as data is written to cells
    AlpGet_insider_purchases = "Data retrieved and written to cells."
    
    Set xmlhttp = Nothing
    Set json = Nothing
End Function
