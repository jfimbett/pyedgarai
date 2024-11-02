
Function AlpGet_Financials_Wrapper(ticker As String, api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim item As Variant
    Dim row As Long
    Dim col As Long
    Dim key As Variant
    Dim index As Variant
    
    ' Set the endpoint URL
    url = "http://localhost:5000/financials?ticker=" & ticker & "&api_token=" & api_token
    
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
    
    ' Set starting row and column for the output
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Display jsonResponse keys as headers
    Set data = jsonResponse("data")
    
    ' Write headers
    For Each key In data
        If key <> "index" Then
            Cells(row, col).Value = key
            col = col + 1
        End If
    Next key
    
    ' Output data
    row = row + 1
    For Each index In data("index")
        col = ActiveCell.Column
        For Each key In data
            If key <> "index" Then
                Cells(row, col).Value = data(key)(Application.Match(index, data("index"), 0) - 1)
                col = col + 1
            End If
        Next key
        row = row + 1
    Next index
    
    AlpGet_Financials_Wrapper = "Success"

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Financials(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Financials_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_Financials = result
End Function
