
Function AlpGet_InsiderTransactions(ticker As String, api_token As String) As Variant
    Dim url As String
    Dim xml As Object
    Dim http As Object
    Dim jsonResponse As Object
    Dim data As Object
    Dim cell As Range
    Dim r As Long, c As Long

    url = "http://127.0.0.1:5000/insider_transactions?ticker=" & ticker & "&api_token=" & api_token

    Set xml = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    Set http = CreateObject("MSXML2.DOMDocument")
    
    xml.Open "GET", url, False
    xml.setRequestHeader "accept", "application/json"
    xml.send

    If xml.Status = 200 Then
        Set jsonResponse = JsonConverter.ParseJson(xml.responseText)
        
        If Not jsonResponse Is Nothing Then
            Set data = jsonResponse("data")
            Set cell = Application.Caller.Cells(1, 1)
            
            r = 0
            For Each key In data.Keys
                c = 0
                cell.Offset(r, c).Value = key
                c = c + 1
                For Each item In data(key)
                    cell.Offset(r, c).Value = item
                    c = c + 1
                Next item
                r = r + 1
            Next key
        End If
    Else
        AlpGet_InsiderTransactions = "Error: " & xml.Status & " - " & xml.StatusText
    End If

End Function

Note: To run this code, you will need a JSON parser for VBA, such as the `JsonConverter` module, which you can get from the VBA-JSON library.