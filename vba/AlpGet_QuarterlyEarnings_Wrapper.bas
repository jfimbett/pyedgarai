
Function AlpGet_QuarterlyEarnings_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object

    ' Set the endpoint URL
    url = "http://localhost:5000/quarterly_earnings?ticker=" & ticker & "&api_token=" & api_token

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
    Dim data As Variant
    data = jsonResponse("data")
    
    Dim startRow As Long
    Dim startCol As Long
    startRow = ActiveCell.Row
    startCol = ActiveCell.Column

    ' If 'data' is a string, directly place it
    If VarType(data) = vbString Then
        Cells(startRow, startCol).Value = data
    Else
        ' Iterate over each item in the 'data' array and write to the sheet
        Dim item As Variant, row As Long, col As Long
        row = startRow
        col = startCol

        Dim keys As Variant
        Dim key As Variant

        ' Get the keys from the first item of data to write headers
        If TypeName(data) = "Collection" Then
            For Each key In data(1).keys
                Cells(row, col).Value = key
                col = col + 1
            Next key
            
            row = row + 1
            col = startCol

            ' Write data
            For Each item In data
                For Each key In item.keys
                    Cells(row, col).Value = item(key)
                    col = col + 1
                Next key
                row = row + 1
                col = startCol
            Next item
        End If
    End If

    AlpGet_QuarterlyEarnings_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_QuarterlyEarnings(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_QuarterlyEarnings_Wrapper(" & Chr(34) & ticker & Chr(34) & ", " & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_QuarterlyEarnings = result
End Function
