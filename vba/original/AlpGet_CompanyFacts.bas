
Function AlpGet_CompanyFacts(cik As String, api_token As String) As Variant
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim cell As Range
    Dim startCell As Range
    Dim i As Long, j As Long
    Dim keys As Object
    Dim dict As Object
    Dim subDict As Object
    Dim units As Object
    Dim item As Object
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://127.0.0.1:5000/company_facts?cik=" & cik & "&api_token=" & api_token
    
    ' Send HTTP request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.Send
    
    ' Get response text
    response = http.responseText
    
    ' Parse JSON response
    Set json = JsonConverter.ParseJson(response)
    
    ' Get the starting cell
    Set startCell = Application.Caller
    
    ' If response is a dictionary or a list of dictionaries, create a table
    If VarType(json) = vbObject Then
        Set keys = json.Keys
        ' Assuming the response is a dictionary with the top-level keys being "cik", "entityName", "facts"
        i = 0
        For Each key In keys
            Set dict = json(key)
            If TypeName(dict) = "Dictionary" And key = "facts" Then
                For Each subKey In dict.Keys
                    Set subDict = dict(subKey)
                    If TypeName(subDict) = "Dictionary" Then
                        For Each unitKey In subDict("units").Keys
                            Set units = subDict("units")(unitKey)
                            For Each item In units
                                ' Write the table headers
                                If i = 0 Then
                                    For j = 0 To item.Count - 1
                                        startCell.Offset(0, j).Value = item.Keys(j)
                                    Next j
                                End If
                                ' Write each row of data
                                For j = 0 To item.Count - 1
                                    startCell.Offset(i + 1, j).Value = item.Items(j)
                                Next j
                                i = i + 1
                            Next item
                        Next unitKey
                    End If
                Next subKey
            Else
                ' Write single value responses directly to the cell
                startCell.Offset(0, i).Value = CStr(json(key))
            End If
        Next key
    Else
        ' If response is a single value, write it directly to the cell
        startCell.Value = CStr(json)
    End If
    
    Set AlpGet_CompanyFacts = response

Cleanup:
    Set http = Nothing
    Set json = Nothing
    Set keys = Nothing
    Set dict = Nothing
    Set subDict = Nothing
    Set units = Nothing
End Function


Ensure that "JsonConverter" is included in your VBA project to parse JSON correctly. You can get "JsonConverter" from https://github.com/VBA-tools/VBA-JSON.