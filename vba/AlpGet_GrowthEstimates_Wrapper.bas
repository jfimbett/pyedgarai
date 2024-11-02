
Function AlpGet_GrowthEstimates_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim item As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/growth_estimates?ticker=" & ticker & "&api_token=" & api_token

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
    Dim headers As Variant
    headers = data("index")
    Dim header As Variant
    Dim i As Long
    
    For i = LBound(headers) To UBound(headers)
        Cells(row, col + i).Value = headers(i)
    Next i

    ' Iterate over each item in the 'data' and write to the sheet
    row = row + 1
    For Each header In headers
        Cells(row, col).Value = header
        For i = LBound(data.keys) + 1 To UBound(data.keys)
            Cells(row, col + i - 1).Value = data(data.keys(i))(Application.WorksheetFunction.Match(header, headers, 0) - 1)
        Next i
        row = row + 1
    Next header

    AlpGet_GrowthEstimates_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_GrowthEstimates(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_GrowthEstimates_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_GrowthEstimates = result
End Function
