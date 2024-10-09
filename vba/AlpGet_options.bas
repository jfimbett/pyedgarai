
Function AlpGet_options(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim dataArray As Variant
    Dim i As Integer

    ' Initialize the URL with passed parameters
    url = "http://127.0.0.1:5000/options?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Make the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Check if "data" key exists in the response
    If Not jsonResponse("data") Is Nothing Then
        ' Convert the data to an array
        dataArray = jsonResponse("data")

        ' Output the array as a table starting at the called cell
        For i = LBound(dataArray) To UBound(dataArray)
            ActiveCell.Offset(i, 0).Value = dataArray(i)
        Next i
    Else
        ActiveCell.Value = "No data available"
    End If

    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
End Function


Note: Make sure to have the JSON parser code (like `JsonConverter.bas`) imported in your VBA environment to use the `JsonConverter.ParseJson` function. JSON parsing libraries can be found on platforms like GitHub, such as `VBA-JSON`.