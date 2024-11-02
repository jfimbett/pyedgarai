
Function AlpGet_Account_Wrapper(units As String, account As String, frame As String, taxonomy As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://127.0.0.1:5000/account?units=" & units & "&account=" & account & "&frame=" & frame & "&taxonomy=" & taxonomy & "&api_token=" & api_token

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
    Cells(row, col).Value     = "accn"
    Cells(row, col + 1).Value = "cik"
    Cells(row, col + 2).Value = "end"
    Cells(row, col + 3).Value = "entityName"
    Cells(row, col + 4).Value = "loc"
    Cells(row, col + 5).Value = "start"
    Cells(row, col + 6).Value = "val"

    ' Iterate over each item in the 'data' array and write to the sheet
    Dim item As Variant
    For Each item In data
        row = row + 1
        Cells(row, col).Value     = item("accn")
        Cells(row, col + 1).Value = item("cik")
        Cells(row, col + 2).Value = item("end")
        Cells(row, col + 3).Value = item("entityName")
        Cells(row, col + 4).Value = item("loc")
        Cells(row, col + 5).Value = item("start")
        Cells(row, col + 6).Value = item("val")
    Next item

    AlpGet_Account_Wrapper = units & "-" & account & "-" & frame & "-" & taxonomy

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Account(units As String, account As String, frame As String, taxonomy As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Account_Wrapper(""" & units & """, """ & account & """, """ & frame & """, """ & taxonomy & """, """ & api_token & """)")
    AlpGet_Account = result
End Function
