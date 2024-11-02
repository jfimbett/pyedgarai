
Function AlpGet_BasicInfo_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler

    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/basic_info?ticker=" & ticker & "&api_token=" & api_token

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
    
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write headers
    Dim key As Variant
    Dim keysIndex As Long
    keysIndex = 1
    For Each key In data.Keys
        Cells(row, col + keysIndex - 1).Value = key
        keysIndex = keysIndex + 1
    Next key

    row = row + 1
    keysIndex = 1
    ' Write values
    For Each key In data.Keys
        Cells(row, col + keysIndex - 1).Value = data(key)
        keysIndex = keysIndex + 1
    Next key

    AlpGet_BasicInfo_Wrapper = ticker & "-" & api_token

Exit Function

ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function

End Function

Function AlpGet_BasicInfo(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_BasicInfo_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_BasicInfo = result
End Function
