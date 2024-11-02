
Function AlpGet_Splits_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long
    
    ' Set the endpoint URL
    url = "http://localhost:5000/splits?ticker=" & ticker & "&api_token=" & api_token
    
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
    
    ' Get the data from the response
    Set data = jsonResponse("data")
    
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value = "Date"
    Cells(row, col + 1).Value = "Stock Splits"
    
    ' Write data to sheet
    Dim i As Long
    For i = LBound(data("Date")) To UBound(data("Date"))
        row = row + 1
        Cells(row, col).Value = data("Date")(i)
        Cells(row, col + 1).Value = data("Stock Splits")(i)
    Next i
    
    AlpGet_Splits_Wrapper = ticker & "-" & api_token

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Splits(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Splits_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Splits = result
End Function
