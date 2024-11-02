
Function AlpGet_RecommendationsSummary_Wrapper(ticker As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim row As Long
    Dim col As Long
    Dim i As Integer

    ' Set the endpoint URL
    url = "http://localhost:5000/recommendations_summary?ticker=" & ticker & "&api_token=" & api_token

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
    Cells(row, col).Value = "period"
    Cells(row, col + 1).Value = "strongBuy"
    Cells(row, col + 2).Value = "buy"
    Cells(row, col + 3).Value = "hold"
    Cells(row, col + 4).Value = "sell"
    Cells(row, col + 5).Value = "strongSell"

    ' Write data to cells
    For i = 0 To UBound(data("period"))
        row = row + 1
        Cells(row, col).Value = data("period")(i)
        Cells(row, col + 1).Value = data("strongBuy")(i)
        Cells(row, col + 2).Value = data("buy")(i)
        Cells(row, col + 3).Value = data("hold")(i)
        Cells(row, col + 4).Value = data("sell")(i)
        Cells(row, col + 5).Value = data("strongSell")(i)
    Next i

    AlpGet_RecommendationsSummary_Wrapper = ticker

    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function   
End Function

Function AlpGet_RecommendationsSummary(ticker As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_RecommendationsSummary_Wrapper(" & Chr(34) & ticker & Chr(34) & "," & Chr(34) & api_token & Chr(34) & ")")
    AlpGet_RecommendationsSummary = result
End Function
