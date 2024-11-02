
Function AlpGet_earnings_dates_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim index As Variant
    Dim key As Variant
    Dim row As Long
    Dim col As Long
    Dim dictItem As Object

    ' Set the endpoint URL
    url = "http://localhost:5000/earnings_dates?ticker=" & ticker & "&api_token=" & api_token

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
    Set index = data("index")
    
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write headers
    For i = 1 To index.Count
        Cells(row, col + i).Value = index(i)
    Next i
    
    ' Iterate over each key in the 'data' dictionary and write to the sheet
    For Each key In data.Keys
        If key <> "index" Then
            row = row + 1
            Cells(row, col).Value = key
            Set dictItem = data(key)
            For i = 1 To dictItem.Count
                Cells(row, col + i).Value = dictItem(i)
            Next i
        End If
    Next key

    AlpGet_earnings_dates_Wrapper = ticker & "-" & api_token

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_earnings_dates(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_earnings_dates_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_earnings_dates = result
End Function
