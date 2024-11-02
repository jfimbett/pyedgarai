
Function AlpGet_History_Metadata_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/history_metadata?ticker=" & ticker & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Display jsonResponse (assuming it's a dictionary or a list of dictionaries)
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    Dim item As Variant
    If TypeName(jsonResponse) = "Collection" Then
        ' Write headers
        Dim key As Variant
        Dim headerCol As Long: headerCol = col
        For Each key In jsonResponse(1).Keys
            Cells(row, headerCol).Value = key
            headerCol = headerCol + 1
        Next key

        ' Iterate over each item and write to the sheet
        row = row + 1
        For Each item In jsonResponse
            Dim valueCol As Long: valueCol = col
            For Each key In item.Keys
                Cells(row, valueCol).Value = item(key)
                valueCol = valueCol + 1
            Next key
            row = row + 1
        Next item
    End If

    AlpGet_History_Metadata_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_History_Metadata(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_History_Metadata_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_History_Metadata = result
End Function
