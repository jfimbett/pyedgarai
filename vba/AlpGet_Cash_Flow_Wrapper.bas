
Function AlpGet_Cash_Flow_Wrapper(ticker As String, api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim headers As Variant
    Dim row As Long
    Dim col As Long
    Dim item As Variant
    Dim header As Variant

    ' Set the endpoint URL
    url = "http://localhost:5000/cash_flow?ticker=" & ticker & "&api_token=" & api_token

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

    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers
    headers = data.Keys
    For Each header In headers
        Cells(row, col).Value = header
        col = col + 1
    Next header

    ' Iterate over each item index
    For i = 1 To UBound(data(headers(0)))
        row = row + 1
        col = ActiveCell.Column
        For Each header In headers
            Cells(row, col).Value = data(header)(i)
            col = col + 1
        Next header
    Next i

    AlpGet_Cash_Flow_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Cash_Flow(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Cash_Flow_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Cash_Flow = result
End Function
