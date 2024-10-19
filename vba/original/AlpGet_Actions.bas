
Function AlpGet_Actions(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim jsonResponse As Object
    Dim data As Object
    Dim index As Variant
    Dim key As Variant
    Dim arr() As Variant
    Dim r As Integer, c As Integer
    
    ' Create the request URL
    url = "http://127.0.0.1:5000/actions?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create HTTP request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    Set data = jsonResponse("data")
    
    ' Set the initial cell for output
    Dim startRow As Integer
    Dim startCol As Integer
    startRow = Application.Caller.Row
    startCol = Application.Caller.Column
    
    ' Write index to the cell
    index = data("index")
    For c = LBound(index) To UBound(index)
        Cells(startRow, startCol + c).Value = index(c)
    Next c
    
    ' Write data to cells
    r = 1
    For Each key In data.Keys
        If key <> "index" Then
            Cells(startRow + r, startCol).Value = key
            arr = data(key)
            For c = LBound(arr) To UBound(arr)
                Cells(startRow + r, startCol + 1 + c).Value = arr(c)
            Next c
            r = r + 1
        End If
    Next key
End Function


To use this function, make sure to include a JSON parser like `VBA-JSON` in your environment to handle the `JsonConverter.ParseJson` function. The function will place the data starting from the cell where it's called. It will create a header row with "Dividends" and "Stock Splits" and fill in the subsequent rows with the corresponding data.