
Function AlpGet_fast_info(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim i As Integer
    Dim header As Range

    ' Initialize the URL
    url = "http://127.0.0.1:5000/fast_info?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHttpRequest object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Open the request
    http.Open "GET", url, False

    ' Set the request headers
    http.setRequestHeader "accept", "application/json"

    ' Send the request
    http.Send

    ' Get the response text
    jsonResponse = http.ResponseText

    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)

    ' Check if response is a dictionary
    If TypeName(json) = "Dictionary" Then
        ' Get the starting cell
        Set header = Application.Caller

        ' Loop through the keys
        i = 0
        For Each key In json.Keys
            ' Write key to cell
            header.Offset(0, i).Value = key
            ' Write value to cell
            header.Offset(1, i).Value = json(key)
            i = i + 1
        Next key
    End If
End Function


**Note:** This code requires a JSON parser for VBA. You can use the JSON conversion library by adding the module "JsonConverter.bas" to your project. It can be found in various VBA JSON repositories like [VBA-JSON](https://github.com/VBA-tools/VBA-JSON).