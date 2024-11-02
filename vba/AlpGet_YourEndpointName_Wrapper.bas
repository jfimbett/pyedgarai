
Function AlpGet_YourEndpointName_Wrapper(param1 As String, param2 As String, param3 As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://your_api_endpoint_url?" & "param1=" & param1 & "&param2=" & param2 & "&param3=" & param3 & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'data' key exists in the response
    If Not jsonResponse.Exists("data") Then Exit Function

    ' Display jsonResponse
    Set data = jsonResponse("data")

    row = ActiveCell.Row + 1
    col = ActiveCell.Column

    ' Write headers
    Cells(row, col).Value = "key1"
    Cells(row, col + 1).Value = "key2"
    Cells(row, col + 2).Value = "key3"

    ' Iterate over each item in the 'data' array and write to the sheet
    Dim item As Variant
    For Each item In data
        row = row + 1
        Cells(row, col).Value = item("key1")
        Cells(row, col + 1).Value = item("key2")
        Cells(row, col + 2).Value = item("key3")
    Next item

    AlpGet_YourEndpointName_Wrapper = param1 & "-" & param2 & "-" & param3

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_YourEndpointName(param1 As String, param2 As String, param3 As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_YourEndpointName_Wrapper(" & Chr(34) & param1 & Chr(34) & ", " & Chr(34) & param2 & Chr(34) & ", " & Chr(34) & param3 & Chr(34) & ", " & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_YourEndpointName = result
End Function
