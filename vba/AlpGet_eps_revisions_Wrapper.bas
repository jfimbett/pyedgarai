
Function AlpGet_eps_revisions_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/eps_revisions?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value     = "index"
    Cells(row, col + 1).Value = "0q"
    Cells(row, col + 2).Value = "+1q"
    Cells(row, col + 3).Value = "0y"
    Cells(row, col + 4).Value = "+1y"
    
    row = row + 1

    ' Iterate over each item in the 'data' array and write to the sheet
    Dim idx As Variant
    For Each idx In data("index")
        Cells(row, col).Value     = idx
        Cells(row, col + 1).Value = data("0q")(Application.Match(idx, data("index"), 0))
        Cells(row, col + 2).Value = data("+1q")(Application.Match(idx, data("index"), 0))
        Cells(row, col + 3).Value = data("0y")(Application.Match(idx, data("index"), 0))
        Cells(row, col + 4).Value = data("+1y")(Application.Match(idx, data("index"), 0))
        row = row + 1
    Next idx

    AlpGet_eps_revisions_Wrapper = ticker & "-" & api_token

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_eps_revisions(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_eps_revisions_Wrapper(""" & ticker & """, """ & api_token & """)")
    AlpGet_eps_revisions = result
End Function
