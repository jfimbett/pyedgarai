
Function AlpGet_YourEndpoint_Wrapper(param1 As String, param2 As String, param3 As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://example.com/yourEndpoint?param1=" & param1 & "&param2=" & param2 & "&param3=" & param3 & "&api_token=" & api_token

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

    ' Assume the response is a dictionary with these keys
    ' Write headers
    Cells(row, col).Value     = "key1"
    Cells(row, col + 1).Value = "key2"
    Cells(row, col + 2).Value = "key3"

    ' Iterate over each item in the 'data' array and write to the sheet
    Dim item As Variant
    For Each item In data
        row = row + 1
        Cells(row, col).Value     = item("key1")
        Cells(row, col + 1).Value = item("key2")
        Cells(row, col + 2).Value = item("key3")
    Next item

    AlpGet_YourEndpoint_Wrapper = param1 & "-" & param2 & "-" & param3

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_YourEndpoint(param1 As String, param2 As String, param3 As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_YourEndpoint_Wrapper(""" & param1 & """, """ & param2 & """, """ & param3 & """, """ & api_token & """)")
    AlpGet_YourEndpoint = result
End Function
