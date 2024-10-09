
Function AlpGet_earnings_history(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim ws As Worksheet
    Dim cell As Range
    Dim data As Variant
    Dim i As Long, j As Long
    
    ' Create an instance of the WinHttpRequest.5.1 object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    ' Format the URL with the provided ticker and api_token
    url = "http://127.0.0.1:5000/earnings_history?ticker=" & ticker & "&api_token=" & api_token
    
    ' Open the HTTP request
    http.Open "GET", url, False
    ' Set the request header for JSON response
    http.SetRequestHeader "accept", "application/json"
    ' Send the HTTP request
    http.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Set the starting cell for the output (the cell where the function was called)
    Set ws = Application.Caller.Worksheet
    Set cell = Application.Caller
    
    ' Get the data dictionary from the JSON response
    If Not jsonResponse Is Nothing Then
        ' Ensure the response has "data"
        If Not jsonResponse("data") Is Nothing Then
            ' Convert the "data" object to a 2D array for easier processing
            data = jsonResponse("data")
            
            ' Loop through the JSON response keys
            j = 0
            For Each key In data
                ' Write the date/time key
                cell.Offset(0, j).Value = key
                i = 1
                ' Write the corresponding values for the key
                For Each value In data(key)
                    cell.Offset(i, j).Value = value
                    i = i + 1
                Next value
                j = j + 1
            Next key
        End If
    End If
End Function


Make sure to include a JSON parser in your VBA environment, such as `JsonConverter`, which you can find at: https://github.com/VBA-tools/VBA-JSON. This parser is necessary for handling JSON responses in VBA.