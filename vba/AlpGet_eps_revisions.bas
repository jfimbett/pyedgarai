
Function AlpGet_eps_revisions(ticker As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim jsonResponse As String
    Dim json As Object
    Dim data As Object
    Dim key As Variant
    Dim arr() As Variant
    Dim i As Integer
    Dim j As Integer

    ' Create a new XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Construct the URL
    url = "http://127.0.0.1:5000/eps_revisions?ticker=" & ticker & "&api_token=" & api_token
    
    ' Make the GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    ' Get the response
    jsonResponse = http.responseText
    
    ' Parse the JSON response
    Set json = JsonConverter.ParseJson(jsonResponse)
    
    ' Navigate to the appropriate section of the JSON
    Set data = json("data")
    
    ' Determine the size of the table
    Dim rowCount As Integer
    Dim colCount As Integer
    rowCount = data("index").Count
    colCount = 0
    For Each key In data
        colCount = colCount + 1
    Next key
    
    ' Initialize the array
    ReDim arr(rowCount, colCount)
    
    ' Fill the array with data
    i = 0
    For Each key In data
        j = 0
        For Each val In data(key)
            If IsNull(val) Then
                arr(j, i) = "null"
            Else
                arr(j, i) = val
            End If
            j = j + 1
        Next val
        i = i + 1
    Next key
    
    ' Output to the sheet
    Dim rng As Range
    Set rng = Application.Caller
    ' Write headers
    For i = 0 To colCount - 1
        rng.Offset(0, i).Value = key
    Next i
    ' Write data
    For j = 0 To rowCount - 1
        For i = 0 To colCount - 1
            rng.Offset(j + 1, i).Value = arr(j, i)
        Next i
    Next j
    
End Function


Please ensure that you have a JSON parser like `JsonConverter` installed in your VBA environment. You can find `JsonConverter` by searching for "VBA JSON parser" online and follow the instructions to install it in your VBA project.