
Function AlpGet_QuarterlyFinancials_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim key As Variant
    Dim index As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/quarterly_financials?ticker=" & ticker & "&api_token=" & api_token

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

    ' Get 'data' from the response
    Set data = jsonResponse("data")
    
    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers
    Dim i As Integer
    i = 1
    For Each key In data
        Cells(row, col + i).Value = key
        i = i + 1
    Next key

    ' Write data to the sheet
    row = row + 1
    For Each index In data("index")
        Cells(row, col).Value = index
        i = 1
        For Each key In data
            If key <> "index" Then
                If Not IsEmpty(data(key)(row - ActiveCell.Row)) Then
                    Cells(row, col + i).Value = data(key)(row - ActiveCell.Row)
                End If
            End If
            i = i + 1
        Next key
        row = row + 1
    Next index
    
    AlpGet_QuarterlyFinancials_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_QuarterlyFinancials(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_QuarterlyFinancials_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_QuarterlyFinancials = result
End Function
