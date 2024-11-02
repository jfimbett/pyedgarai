
Function AlpGet_stocks_data_Wrapper(tickers As Variant, start_date As String, end_date As String, api_token As String) As String
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim i As Long
    Dim row As Long
    Dim col As Long
    Dim ticker As Variant
    Dim tickersParam As String

    ' Construct the tickers parameter
    tickersParam = ""
    For Each ticker In tickers
        tickersParam = tickersParam & "tickers=" & ticker & "&"
    Next ticker
    tickersParam = Left(tickersParam, Len(tickersParam) - 1) ' Remove the trailing '&'

    ' Set the endpoint URL
    url = "http://localhost:5000/stocks_data?" & tickersParam & "&start_date=" & start_date & "&end_date=" & end_date & "&api_token=" & api_token

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
    Set data = jsonResponse("data")("Adj Close")

    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write headers
    Cells(row, col).Value = "Adj Close"

    ' Iterate over each item in the 'Adj Close' array and write to the sheet
    For i = LBound(data) To UBound(data)
        row = row + 1
        Cells(row, col).Value = data(i)
    Next i

    AlpGet_stocks_data_Wrapper = Join(tickers, ", ") & "-" & start_date & "-" & end_date

Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_stocks_data(tickers As Variant, start_date As String, end_date As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_stocks_data_Wrapper(" & Join(Application.Index(tickers, 0), ", ") & ",""" & start_date & """,""" & end_date & """,""" & api_token & """)")
    AlpGet_stocks_data = result
End Function
