
Function AlpGet_valuation_metrics_Wrapper(tickers As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim avgMultiples As Variant
    Dim variables As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/valuation_metrics?" & "tickers=" & Replace(tickers, ",", "&tickers=") & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    row = ActiveCell.Row
    col = ActiveCell.Column

    ' Write avg_multiples headers and data
    If jsonResponse.Exists("avg_multiples") Then
        Set avgMultiples = jsonResponse("avg_multiples")
        Cells(row, col).Value = "Metric"
        Cells(row, col + 1).Value = "Value"
        row = row + 1
        Cells(row, col).Value = "enterpriseToEbitda"
        Cells(row, col + 1).Value = avgMultiples("enterpriseToEbitda")
        row = row + 1
        Cells(row, col).Value = "priceToBook"
        Cells(row, col + 1).Value = avgMultiples("priceToBook")
        row = row + 1
        Cells(row, col).Value = "priceToEarnings"
        Cells(row, col + 1).Value = avgMultiples("priceToEarnings")
        row = row + 2
    End If

    ' Write variables headers and data
    If jsonResponse.Exists("variables") Then
        Set variables = jsonResponse("variables")

        ' Write headers
        Cells(row, col).Value = "Ticker"
        Cells(row, col + 1).Value = "Current Price"
        Cells(row, col + 2).Value = "Enterprise To EBITDA"
        Cells(row, col + 3).Value = "Enterprise Value"
        Cells(row, col + 4).Value = "EPS"
        Cells(row, col + 5).Value = "Market Cap"
        Cells(row, col + 6).Value = "Price To Book"
        Cells(row, col + 7).Value = "Price To Earnings"
        Cells(row, col + 8).Value = "Shares Outstanding"

        Dim item As Variant
        For Each item In variables
            row = row + 1
            Cells(row, col).Value = item("ticker")
            Cells(row, col + 1).Value = item("currentPrice")
            Cells(row, col + 2).Value = item("enterpriseToEbitda")
            Cells(row, col + 3).Value = item("enterpriseValue")
            Cells(row, col + 4).Value = item("eps")
            Cells(row, col + 5).Value = item("marketCap")
            Cells(row, col + 6).Value = item("priceToBook")
            Cells(row, col + 7).Value = item("priceToEarnings")
            Cells(row, col + 8).Value = item("sharesOutstanding")
        Next item
    End If

    AlpGet_valuation_metrics_Wrapper = Join(Split(tickers, ","), " & ") & " fetched."
    Exit Function
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_valuation_metrics(tickers As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_valuation_metrics_Wrapper(""" & tickers & """, """ & api_token & """)")
    AlpGet_valuation_metrics = result
End Function
