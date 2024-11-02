
Function AlpGet_EarningsHistory_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim indexData As Variant
    Dim dateKey As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/earnings_history?ticker=" & ticker & "&api_token=" & api_token

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

    ' Extract index and data
    Set data = jsonResponse("data")
    indexData = data("index")
    
    row = ActiveCell.Row + 1
    col = ActiveCell.Column
    
    ' Write headers
    Cells(row, col).Value = "Date"
    Dim indexKey As Variant
    For Each indexKey In indexData
        col = col + 1
        Cells(row, col).Value = indexKey
    Next indexKey

    ' Iterate over each date in the 'data' object and write to the sheet
    For Each dateKey In data.Keys
        If dateKey <> "index" Then
            row = row + 1
            col = ActiveCell.Column
            Cells(row, col).Value = dateKey
            Dim i As Integer
            For i = LBound(data(dateKey)) To UBound(data(dateKey))
                col = col + 1
                Cells(row, col).Value = data(dateKey)(i)
            Next i
        End If
    Next dateKey

    AlpGet_EarningsHistory_Wrapper = ticker & "-" & api_token
    Exit Function

ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_EarningsHistory(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_EarningsHistory_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_EarningsHistory = result
End Function
