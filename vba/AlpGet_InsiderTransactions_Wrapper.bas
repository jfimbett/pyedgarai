
Function AlpGet_InsiderTransactions_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long
    
    ' Set the endpoint URL
    url = "http://localhost:5000/insider_transactions?ticker=" & ticker & "&api_token=" & api_token
    
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
    Cells(row, col).Value = "Shares"
    Cells(row, col + 1).Value = "URL"
    Cells(row, col + 2).Value = "Text"
    Cells(row, col + 3).Value = "Insider"
    Cells(row, col + 4).Value = "Position"
    Cells(row, col + 5).Value = "Transaction"
    Cells(row, col + 6).Value = "Start Date"
    Cells(row, col + 7).Value = "Ownership"
    Cells(row, col + 8).Value = "Value"
    
    Dim i As Long
    For i = 1 To UBound(data("Shares"))
        row = row + 1
        Cells(row, col).Value = data("Shares")(i)
        Cells(row, col + 1).Value = data("URL")(i)
        Cells(row, col + 2).Value = data("Text")(i)
        Cells(row, col + 3).Value = data("Insider")(i)
        Cells(row, col + 4).Value = data("Position")(i)
        Cells(row, col + 5).Value = data("Transaction")(i)
        Cells(row, col + 6).Value = data("Start Date")(i)
        Cells(row, col + 7).Value = data("Ownership")(i)
        Cells(row, col + 8).Value = data("Value")(i)
    Next i
    
    AlpGet_InsiderTransactions_Wrapper = ticker & "-" & api_token
    
    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_InsiderTransactions(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_InsiderTransactions_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_InsiderTransactions = result
End Function
