
Function AlpGet_RevenueEstimate_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim index As Variant
    Dim field As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/revenue_estimate?ticker=" & ticker & "&api_token=" & api_token

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

    ' Get 'data'
    Set data = jsonResponse("data")

    ' Start writing from the next row
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    ' Write headers
    index = data("index")
    For Each field In index
        Cells(row, col).Value = field
        col = col + 1
    Next field

    ' Reset column position
    col = ActiveCell.Column
    
    ' Write values for each period
    For Each field In data
        If field <> "index" Then
            row = row + 1
            ' Write the row header (the periods)
            Cells(row, col).Value = field
            ' Write the values
            For i = 0 To UBound(data(field))
                Cells(row, col + 1 + i).Value = data(field)(i)
            Next i
        End If
    Next field

    AlpGet_RevenueEstimate_Wrapper = ticker & "-" & api_token
    Exit Function

ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_RevenueEstimate(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_RevenueEstimate_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_RevenueEstimate = result
End Function
