
Function AlpGet_valuation_metrics(api_url As String, tickers As String, api_token As String)

    ' Set up variables
    Dim http As Object
    Dim jsonResp As Object
    Dim json As Object
    Dim vars As Object
    Dim cell As Range
    Dim i As Integer, key As Variant

    ' Initialize HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Construct request URL
    Dim requestUrl As String
    requestUrl = api_url & "/valuation_metrics?tickers=" & tickers & "&api_token=" & api_token

    ' Initialize request
    With http
        .Open "GET", requestUrl, False
        .setRequestHeader "accept", "application/json"
        .send
    End With

    ' Parse JSON response
    Set jsonResp = JsonConverter.ParseJson(http.responseText)

    ' Set the starting point for writing the response
    Set cell = Application.Caller

    If Not jsonResp Is Nothing Then

        ' Handle "avg_multiples"
        Set json = jsonResp("avg_multiples")
        If Not json Is Nothing Then
            i = 0
            For Each key In json.keys
                cell.Offset(i, 0).Value = key
                cell.Offset(i, 1).Value = json(key)
                i = i + 1
            Next key

            ' Move starting cell down by the number of avg_multiples to start the variables table
            Set cell = cell.Offset(i + 1, 0)
        End If

        ' Handle "variables"
        Set vars = jsonResp("variables")
        If Not vars Is Nothing Then
            ' Write headers
            i = 0
            For Each key In vars(1).keys    ' Assumes all dictionaries have the same keys
                cell.Offset(0, i).Value = key
                i = i + 1
            Next key

            ' Write values
            i = 1
            For Each json In vars
                Dim j As Integer
                j = 0
                For Each key In json.keys
                    cell.Offset(i, j).Value = json(key)
                    j = j + 1
                Next key
                i = i + 1
            Next json
        End If

    End If

    ' Cleanup
    Set http = Nothing
    Set jsonResp = Nothing
    Set json = Nothing
    
End Function

