
Function AlpGet_mutualfund_holders(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim field As Variant
    Dim currentRow As Integer
    Dim i As Integer
    Dim key As Variant

    ' Create the URL with parameters
    url = "http://127.0.0.1:5000/mutualfund_holders?ticker=" & ticker & "&api_token=" & api_token

    ' Create the HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Send the GET request
    With http
        .Open "GET", url, False
        .setRequestHeader "Accept", "application/json"
        .send
        response = .responseText
    End With
    
    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(response)
    
    ' Get the data dictionary
    Set data = json("data")
    
    ' Write the data to the Excel sheet
    currentRow = Application.Caller.Row
    i = 0
    For Each key In data.Keys
        ' Write the headers
        Cells(currentRow, Application.Caller.Column + i).Value = key
        ' Write the data under each header
        For Each field In data(key)
            Cells(currentRow + 1, Application.Caller.Column + i).Value = field
            currentRow = currentRow + 1
        Next field
        currentRow = Application.Caller.Row
        i = i + 1
    Next key
End Function


Note: To use the above function, you will need to import the "JsonConverter" library into your VBA environment to handle JSON parsing. You can do this by including the `JsonConverter.bas` file from https://github.com/VBA-tools/VBA-JSON.