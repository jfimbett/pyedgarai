
Function AlpGet_comparables(cik As String, _
                            method As String, _
                            api_token As String, _
                            industry_digits As Integer, _
                            size_interval As Integer, _
                            profitability_interval As Integer, _
                            growth_rate_interval As Integer, _
                            capital_structure_interval As Integer) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim cell As Range
    Dim key As Variant
    Dim jsonData As Variant
    Dim headers As Variant
    Dim i As Integer

    ' Construct the API request URL
    url = "http://127.0.0.1:5000/comparables?" & _
          "cik=" & cik & _
          "&variables_to_compare=industry" & _
          "&variables_to_compare=size" & _
          "&variables_to_compare=profitability" & _
          "&variables_to_compare=growth_rate" & _
          "&variables_to_compare=capital_structure" & _
          "&variables_to_compare=location" & _
          "&extra_variables=GrossProfit" & _
          "&extra_variables=NetIncomeLoss" & _
          "&extra_variables=EarningsPerShareBasic" & _
          "&method=" & method & _
          "&api_token=" & api_token & _
          "&industry_digits=" & industry_digits & _
          "&size_interval=" & size_interval & _
          "&profitability_interval=" & profitability_interval & _
          "&growth_rate_interval=" & growth_rate_interval & _
          "&capital_structure_interval=" & capital_structure_interval

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    http.send

    ' Validate response status
    If http.Status <> 200 Then
        AlpGet_comparables = "Error: " & http.statusText
        Exit Function
    End If

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)

    ' Write the data to Excel starting at the current cell
    Set cell = Application.Caller
    i = 0
    If TypeName(jsonResponse) = "Dictionary" Then
        headers = jsonResponse.Keys
        
        ' Write the headers
        For Each key In headers
            cell.Offset(0, i).Value = key
            i = i + 1
        Next key

        ' Write the data rows
        i = 0
        For Each key In headers
            cell.Offset(1, i).Value = jsonResponse(key)("0")
            i = i + 1
        Next key
    End If

    ' Cleanup
    Set http = Nothing
    Set jsonResponse = Nothing
End Function

