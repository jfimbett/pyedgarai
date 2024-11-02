
Function AlpGet_MutualFund_Holders_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long
    Dim headers As Variant
    Dim i As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/mutualfund_holders?ticker=" & ticker & "&api_token=" & api_token

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
    headers = Array("Date Reported", "Holder", "pctHeld", "Shares", "Value")
    For i = LBound(headers) To UBound(headers)
        Cells(row, col + i).Value = headers(i)
    Next i

    ' Write data to the sheet
    Dim key As Variant
    Dim index As Long
    For index = 0 To UBound(data("Date Reported"))
        row = row + 1
        Cells(row, col).Value = data("Date Reported")(index)
        Cells(row, col + 1).Value = data("Holder")(index)
        Cells(row, col + 2).Value = data("pctHeld")(index)
        Cells(row, col + 3).Value = data("Shares")(index)
        Cells(row, col + 4).Value = data("Value")(index)
    Next index

    AlpGet_MutualFund_Holders_Wrapper = "Success"

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_MutualFund_Holders(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_MutualFund_Holders_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_MutualFund_Holders = result
End Function
