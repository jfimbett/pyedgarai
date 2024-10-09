
Function AlpGet_clean_name(api_url As String, name As String, api_token As String)
    Dim http As Object
    Dim json As Object
    Dim result As String
    Dim cell As Range
    Dim url As String

    ' Concatenate the URL with parameters
    url = api_url & "?name=" & name & "&api_token=" & api_token

    ' Create a new XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Open a connection to the API endpoint
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    
    ' Send the request
    http.send

    ' Get the response
    result = http.responseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(result)

    ' Get the current cell
    Set cell = Application.Caller

    ' Check if the JSON object contains the expected key
    If json.Exists("clean_name") Then
        ' Output the clean_name value to the cell
        cell.Value = json("clean_name")
    End If

    ' Clean up
    Set http = Nothing
    Set json = Nothing
End Function
