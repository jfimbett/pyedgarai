
Function AlpGet_Capital_Gains_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/capital_gains?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if response is a dictionary or list
    If Not IsEmpty(jsonResponse) Then
        If TypeName(jsonResponse) = "Dictionary" Then
            ' Handle dictionary response
            row = ActiveCell.Row
            col = ActiveCell.Column
            
            ' Write headers and data to the sheet
            Dim key As Variant
            For Each key In jsonResponse.Keys
                Cells(row, col).Value = key
                Cells(row + 1, col).Value = jsonResponse(key)
                col = col + 1
            Next key
            
        ElseIf TypeName(jsonResponse) = "Collection" Then
            ' Handle list of dictionaries response
            row = ActiveCell.Row + 1
            col = ActiveCell.Column
            
            ' Assume all dictionaries have the same keys, write headers from the first item
            Dim firstItem As Object
            Set firstItem = jsonResponse(1)
            Dim header As Variant
            Dim i As Long
            i = col
            For Each header In firstItem.Keys
                Cells(row - 1, i).Value = header
                i = i + 1
            Next header
            
            ' Write data to the sheet
            Dim item As Variant
            For Each item In jsonResponse
                For Each key In item.Keys
                    Cells(row, col).Value = item(key)
                    col = col + 1
                Next key
                row = row + 1
                col = ActiveCell.Column
            Next item
        End If
    End If

    AlpGet_Capital_Gains_Wrapper = ticker & "-" & api_token
    
    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Capital_Gains(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Capital_Gains_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Capital_Gains = result
End Function
