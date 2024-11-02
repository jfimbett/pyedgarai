
Function AlpGet_Info_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/info?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value = "Key"
    Cells(row, col + 1).Value = "Value"
    
    Dim key As Variant
    Dim rowNum As Long
    rowNum = row + 1

    ' Iterate over each key in the 'data' dictionary and write to the sheet
    For Each key In data.Keys
        Cells(rowNum, col).Value = key
        Cells(rowNum, col + 1).Value = data(key)
        rowNum = rowNum + 1
    Next key

    AlpGet_Info_Wrapper = ticker

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Info(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Info_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Info = result
End Function
