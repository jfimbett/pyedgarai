
Function AlpGet_News_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/news?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value = "link"
    Cells(row, col + 1).Value = "providerPublishTime"
    Cells(row, col + 2).Value = "publisher"
    Cells(row, col + 3).Value = "title"
    Cells(row, col + 4).Value = "type"
    Cells(row, col + 5).Value = "uuid"

    ' Iterate over each item in the 'data' array and write to the sheet
    Dim item As Variant
    For Each item In data
        row = row + 1
        Cells(row, col).Value = item("link")
        Cells(row, col + 1).Value = item("providerPublishTime")
        Cells(row, col + 2).Value = item("publisher")
        Cells(row, col + 3).Value = item("title")
        Cells(row, col + 4).Value = item("type")
        Cells(row, col + 5).Value = item("uuid")
    Next item

    AlpGet_News_Wrapper = ticker & "-" & api_token

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_News(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_News_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_News = result
End Function
