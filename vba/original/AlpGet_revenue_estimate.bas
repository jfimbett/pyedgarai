
Function AlpGet_revenue_estimate(api_url As String, ticker As String, api_token As String) As Variant
    Dim requestUrl As String
    Dim httpRequest As Object
    Dim jsonResponse As String
    Dim jsonResponseObj As Object
    Dim dataObj As Object
    Dim indexArray As Variant
    Dim period As Variant
    Dim i As Integer, j As Integer
    
    ' Construct the request URL
    requestUrl = api_url & "?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create the HTTP request
    Set httpRequest = CreateObject("MSXML2.XMLHTTP")
    httpRequest.Open "GET", requestUrl, False
    httpRequest.setRequestHeader "accept", "application/json"
    httpRequest.send
    
    ' Get the response
    jsonResponse = httpRequest.responseText
    
    ' Parse the JSON response
    Set jsonResponseObj = JsonConverter.ParseJson(jsonResponse)
    Set dataObj = jsonResponseObj("data")
    
    ' Get index array
    indexArray = dataObj("index")
    
    ' Write the table to Excel starting from the cell where the function is called
    With Application.Caller
        ' Write header row
        For j = LBound(indexArray) To UBound(indexArray)
            .Offset(0, j).Value = indexArray(j)
        Next j
        
        ' Write data rows
        i = 1
        For Each period In dataObj.Keys
            If period <> "index" Then
                .Offset(i, 0).Value = period
                For j = LBound(dataObj(period)) To UBound(dataObj(period))
                    .Offset(i, j + 1).Value = dataObj(period)(j)
                Next j
                i = i + 1
            End If
        Next period
    End With
    
End Function

Make sure to include a JSON parsing library like "JsonConverter" (which can be found on GitHub) to parse the API's JSON response.