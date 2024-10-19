
Function AlpGet_quarterly_cashflow(ticker As String, api_token As String)
    Dim httpRequest As Object
    Dim url As String
    Dim jsonResponse As String
    Dim jsonData As Object
    Dim i As Integer, j As Integer
    Dim headerKeys As Collection
    Dim dataValues As Variant
    
    ' Create the HTTP request object
    Set httpRequest = CreateObject("MSXML2.XMLHTTP")
    
    ' Set the URL with the provided parameters
    url = "http://127.0.0.1:5000/quarterly_cashflow?ticker=" & ticker & "&api_token=" & api_token
    
    ' Open the request and set the headers
    httpRequest.Open "GET", url, False
    httpRequest.setRequestHeader "accept", "application/json"
    
    ' Send the request and get the response text
    httpRequest.Send
    jsonResponse = httpRequest.responseText
    
    ' Parse the JSON response
    Set jsonData = JsonConverter.ParseJson(jsonResponse)
    
    ' Get header keys
    Set headerKeys = New Collection
    For Each key In jsonData("data").Keys
        headerKeys.Add key
    Next key
    
    ' Write headers to the worksheet
    For j = 1 To headerKeys.Count
        Cells(1, j).Value = headerKeys(j)
    Next j
    
    ' Write data to the worksheet
    dataValues = jsonData("data")(headerKeys(1)) ' Just getting the length
    For i = 1 To UBound(dataValues) + 1
        For j = 1 To headerKeys.Count
            Cells(i + 1, j).Value = jsonData("data")(headerKeys(j))(i - 1)
        Next j
    Next i
End Function


Ensure you have the JSON parser library (`JsonConverter`) available in your VBA environment, or you can find a library like `VBA-JSON` online to handle JSON parsing in VBA.