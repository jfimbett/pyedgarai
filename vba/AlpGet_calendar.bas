
Function AlpGet_calendar(ticker As String, api_token As String)

    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim cell As Range
    Dim i As Integer
    
    ' Set up HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/calendar?ticker=" & ticker & "&api_token=" & api_token
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.Send
    
    ' Get the response
    response = http.responseText
    
    ' Parse JSON
    Set json = JsonConverter.ParseJson(response)
    
    ' Assume the function is called in a worksheet cell
    Set cell = Application.Caller
    
    ' Write keys and values to the worksheet starting from the cell where function is called
    i = 0
    Dim key As Variant
    For Each key In json("data")
        cell.Offset(i, 0).Value = key
        If TypeName(json("data")(key)) = "Collection" Then
            cell.Offset(i, 1).Value = Join(json("data")(key).ToArray, ", ")
        Else
            cell.Offset(i, 1).Value = json("data")(key)
        End If
        i = i + 1
    Next key

End Function


**Note:** This code assumes you have the `JsonConverter` module for VBA, which allows VBA to parse JSON objects. JsonConverter can be added by importing the `JsonConverter.bas` file from [this GitHub repository](https://github.com/VBA-tools/VBA-JSON).