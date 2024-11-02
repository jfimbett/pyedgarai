
Function AlpGet_Calendar_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long
    
    ' Set the endpoint URL
    url = "http://localhost:5000/calendar?ticker=" & ticker & "&api_token=" & api_token
    
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
    Cells(row, col).Value     = "Dividend Date"
    Cells(row, col + 1).Value = "Earnings Average"
    Cells(row, col + 2).Value = "Earnings Date"
    Cells(row, col + 3).Value = "Earnings High"
    Cells(row, col + 4).Value = "Earnings Low"
    Cells(row, col + 5).Value = "Ex-Dividend Date"
    Cells(row, col + 6).Value = "Revenue Average"
    Cells(row, col + 7).Value = "Revenue High"
    Cells(row, col + 8).Value = "Revenue Low"
    
    ' Write the data
    row = row + 1
    Cells(row, col).Value     = data("Dividend Date")
    Cells(row, col + 1).Value = data("Earnings Average")
    Cells(row, col + 2).Value = Join(data("Earnings Date"), ", ")
    Cells(row, col + 3).Value = data("Earnings High")
    Cells(row, col + 4).Value = data("Earnings Low")
    Cells(row, col + 5).Value = data("Ex-Dividend Date")
    Cells(row, col + 6).Value = data("Revenue Average")
    Cells(row, col + 7).Value = data("Revenue High")
    Cells(row, col + 8).Value = data("Revenue Low")
    
    AlpGet_Calendar_Wrapper = ticker & "-" & api_token
    
    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Calendar(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Calendar_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Calendar = result
End Function
