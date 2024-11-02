
Function AlpGet_Insider_Purchases_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim columnNames As Variant
    Dim row As Long
    Dim col As Long
    Dim i As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/insider_purchases?ticker=" & ticker & "&api_token=" & api_token

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

    ' Extract data
    Set data = jsonResponse("data")
    
    ' Get starting row and column from the active cell
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write table headers
    columnNames = data("Insider Purchases Last 6m")
    For i = LBound(columnNames) To UBound(columnNames)
        Cells(row, col + i).Value = columnNames(i)
    Next i

    ' Write each column's data from dictionaries
    For i = 0 To UBound(data("Shares"))
        Cells(row + i + 1, col).Value = data("Shares")(i)
        Cells(row + i + 1, col + 1).Value = data("Sales")(i)
        Cells(row + i + 1, col + 2).Value = data("Net Shares Purchased (Sold)")(i)
        Cells(row + i + 1, col + 3).Value = data("Total Insider Shares Held")(i)
        Cells(row + i + 1, col + 4).Value = data("% Net Shares Purchased (Sold)")(i)
        Cells(row + i + 1, col + 5).Value = data("% Buy Shares")(i)
        Cells(row + i + 1, col + 6).Value = data("% Sell Shares")(i)
    Next i

    AlpGet_Insider_Purchases_Wrapper = ticker & "-" & "Data Retrieved"

    Exit Function
    ErrorHandler:
        MsgBox "An error occurred: " & Err.Description & " " & Erl
        Exit Function   
End Function

Function AlpGet_Insider_Purchases(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Insider_Purchases_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_Insider_Purchases = result
End Function
