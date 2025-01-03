
Function AlpGet_Fast_Info_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim key As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/fast_info?ticker=" & ticker & "&api_token=" & api_token

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
    For Each key In data
        Cells(row, col).Value = key
        col = col + 1
    Next key
    
    row = row + 1
    col = ActiveCell.Column
    
    ' Write data
    For Each key In data
        Cells(row, col).Value = data(key)
        col = col + 1
    Next key

    AlpGet_Fast_Info_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_Fast_Info(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Fast_Info_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Fast_Info = result
End Function