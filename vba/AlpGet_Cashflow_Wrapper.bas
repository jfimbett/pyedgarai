
Function AlpGet_Cashflow_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/cashflow?ticker=" & ticker & "&api_token=" & api_token

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

    row = ActiveCell.Row + 1
    col = ActiveCell.Column
    
    ' Write headers
    Dim header As Variant
    Dim i As Integer
    i = 0
    For Each header In data.Keys
        Cells(row, col + i).Value = header
        i = i + 1
    Next header
    
    ' Get length of the index to know rows to write
    Dim index As Variant
    Dim j As Integer
    j = 0
    index = data("index")
    
    ' Iterate over each row in the data dictionary and write to the sheet
    Dim k As Variant
    Dim value As Variant
    For j = 0 To UBound(index)
        row = row + 1
        i = 0
        For Each k In data.Keys
            value = data(k)
            Cells(row, col + i).Value = value(j)
            i = i + 1
        Next k
    Next j

    AlpGet_Cashflow_Wrapper = ticker

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Cashflow(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Cashflow_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_Cashflow = result
End Function
