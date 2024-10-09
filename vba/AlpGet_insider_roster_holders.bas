
Function AlpGet_insider_roster_holders(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim jsonResponse As Object
    Dim data As Object
    Dim dictKey As Variant
    Dim cell As Range
    Dim rowOffset As Long
    Dim columnOffset As Long
    Dim i As Long

    ' Set URL
    url = "http://127.0.0.1:5000/insider_roster_holders?ticker=" & ticker & "&api_token=" & api_token

    ' Create HTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get the response
    response = http.responseText
    
    ' Parse JSON response
    Set jsonResponse = JsonConverter.ParseJson(response)
    
    ' Extract data object
    Set data = jsonResponse("data")
    
    ' Write data to worksheet starting from the cell where the function is called
    Set cell = Application.Caller
    rowOffset = 0

    ' Write headers
    For Each dictKey In data.Keys
        cell.Offset(rowOffset, columnOffset).Value = dictKey
        columnOffset = columnOffset + 1
    Next dictKey

    rowOffset = rowOffset + 1
    columnOffset = 0
    
    ' Write data for each key in the dictionary
    For i = 1 To data("Name").Count
        columnOffset = 0
        For Each dictKey In data.Keys
            cell.Offset(rowOffset, columnOffset).Value = data(dictKey)(i)
            columnOffset = columnOffset + 1
        Next dictKey
        rowOffset = rowOffset + 1
    Next i
    
    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
    Set data = Nothing
End Function


To correctly parse JSON in VBA, you'll need a JSON parsing library like "VBA-JSON" by Tim Hall. Make sure you have it imported and set up in your VBA environment.