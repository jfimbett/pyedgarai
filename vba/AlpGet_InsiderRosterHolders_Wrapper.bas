
Function AlpGet_InsiderRosterHolders_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/insider_roster_holders?ticker=" & ticker & "&api_token=" & api_token

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

    ' Set data
    Set data = jsonResponse("data")
    
    row = ActiveCell.Row + 1
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value = "Name"
    Cells(row, col + 1).Value = "Position"
    Cells(row, col + 2).Value = "URL"
    Cells(row, col + 3).Value = "Most Recent Transaction"
    Cells(row, col + 4).Value = "Latest Transaction Date"
    Cells(row, col + 5).Value = "Shares Owned Directly"
    Cells(row, col + 6).Value = "Position Direct Date"
    
    ' Get the number of entries (using "Name" key for example purposes)
    Dim i As Long
    For i = 1 To UBound(data("Name"))
        row = row + 1
        Cells(row, col).Value = data("Name")(i)
        Cells(row, col + 1).Value = data("Position")(i)
        Cells(row, col + 2).Value = data("URL")(i)
        Cells(row, col + 3).Value = data("Most Recent Transaction")(i)
        Cells(row, col + 4).Value = data("Latest Transaction Date")(i)
        Cells(row, col + 5).Value = data("Shares Owned Directly")(i)
        Cells(row, col + 6).Value = data("Position Direct Date")(i)
    Next i

    AlpGet_InsiderRosterHolders_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_InsiderRosterHolders(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_InsiderRosterHolders_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_InsiderRosterHolders = result
End Function
