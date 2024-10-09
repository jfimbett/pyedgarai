
Function AlpGet_RecommendationsSummary(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim cell As Range
    Dim headers As Variant
    Dim data As Variant
    Dim i As Integer
    Dim j As Integer
    
    ' Construct the URL with the provided arguments
    url = "http://127.0.0.1:5000/recommendations_summary?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Get the starting cell
    Set cell = Application.Caller
    
    ' Prepare headers from the JSON keys
    headers = Array("period", "strongBuy", "buy", "hold", "sell", "strongSell")
    
    ' Write headers to the sheet
    For i = LBound(headers) To UBound(headers)
        cell.Offset(0, i).Value = headers(i)
    Next i
    
    ' Write data to the sheet
    data = jsonResponse("data")
    
    For i = 0 To UBound(data("period"))
        For j = LBound(headers) To UBound(headers)
            cell.Offset(i + 1, j).Value = data(headers(j))(i)
        Next j
    Next i

    ' Return the response to the calling cell
    AlpGet_RecommendationsSummary = "Data written to the sheet"
End Function


Make sure you have a JSON parser, such as `JsonConverter.bas` from VBA-JSON, imported into your VBA environment to allow the JSON parsing to work.