
Function AlpGet_Balance_Sheet_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim indexData As Variant
    Dim key As Variant
    Dim i As Long
    Dim j As Long
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/balance_sheet?ticker=" & ticker & "&api_token=" & api_token

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
    indexData = data("index")
    
    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers
    j = 0
    For Each key In data.Keys
        If key <> "index" Then
            Cells(row, col + j).Value = key
            j = j + 1
        End If
    Next key

    ' Write each row of data
    For i = 0 To UBound(indexData)
        row = row + 1
        Cells(row, col).Value = indexData(i)
        j = 1
        For Each key In data.Keys
            If key <> "index" Then
                If IsObject(data(key)) And i <= UBound(data(key)) Then
                    Cells(row, col + j).Value = data(key)(i)
                End If
                j = j + 1
            End If
        Next key
    Next i

    AlpGet_Balance_Sheet_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_Balance_Sheet(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Balance_Sheet_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Balance_Sheet = result
End Function
