
Function AlpGet_isin(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim http As Object
    Dim jsonResponse As Object
    Dim responseData As Variant
    Dim cell As Range
    
    ' Construct URL with parameters
    url = "http://127.0.0.1:5000/isin?ticker=" & ticker & "&api_token=" & api_token
    
    ' Create a new XMLHTTP object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Initialize request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    
    ' Send the request
    http.Send
    
    ' Parse the response
    Set jsonResponse = JsonConverter.ParseJson(http.responseText)
    
    ' Write output to the cell where the function is called
    Set cell = Application.Caller
    
    ' Check if the response contains data
    If Not jsonResponse Is Nothing Then
        If VBA.TypeName(jsonResponse) = "Collection" Then
            If jsonResponse.Exists("data") Then
                cell.Value = jsonResponse("data")
            End If
        Else
            cell.Value = http.responseText
        End If
    End If
    
    ' Clean up
    Set http = Nothing
    Set jsonResponse = Nothing
    Set cell = Nothing
End Function


Note: This script uses a JSON parser. To use it, you might need to import a JSON library, such as VBA-JSON (https://github.com/VBA-tools/VBA-JSON), into your VBA project in order to use `JsonConverter.ParseJson`.