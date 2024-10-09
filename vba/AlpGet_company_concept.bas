
Function AlpGet_company_concept(cik As String, tag As String, taxonomy As String, api_token As String)

    ' Set variables
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim dict As Object
    Dim i As Long
    Dim col As Long
    Dim resultRow As Long
    Dim cell As Range
    
    ' Create the URL
    url = "http://127.0.0.1:5000/company_concept?cik=" & cik & "&tag=" & tag & "&taxonomy=" & taxonomy & "&api_token=" & api_token
    
    ' Set reference to the current cell where the formula is called
    Set cell = Application.Caller
    
    ' Create the XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Open the request
    http.Open "GET", url, False
    
    ' Set the request headers
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Write JSON data to Excel
    If Not jsonResponse Is Nothing Then
        ' Handle the main keys of the response if needed
        data = jsonResponse("units")("USD")
        
        ' Create headers
        col = 0
        If TypeName(data) = "Collection" And data.Count > 0 Then
            For Each dict In data
                For Each key In dict.keys
                    cell.Offset(0, col).Value = key
                    col = col + 1
                Next key
                Exit For
            Next dict
            
            ' Fill data
            resultRow = 1
            For Each dict In data
                col = 0
                For Each key In dict.keys
                    cell.Offset(resultRow, col).Value = dict(key)
                    col = col + 1
                Next key
                resultRow = resultRow + 1
            Next dict
        End If
        
    End If

End Function


Note: This code assumes you have a JSON parser available, such as `JsonConverter.bas`, which you can find in various open-source VBA JSON parsers online. You need to include this or a similar JSON parsing library in your VBA project for the above function to work.