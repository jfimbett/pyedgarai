
Function AlpGet_income_stmt(ticker As String, api_token As String)
    Dim http As Object
    Dim url As String
    Dim response As String
    Dim json As Object
    Dim data As Object
    Dim key As Variant
    Dim r As Integer, c As Integer

    ' Initialize variables
    url = "http://127.0.0.1:5000/income_stmt?ticker=" & ticker & "&api_token=" & api_token
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' Make HTTP GET request
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send

    ' Get response
    response = http.responseText
    Set json = JsonConverter.ParseJson(response)
    Set data = json("data")

    ' Write response to cells
    r = Application.Caller.Row
    c = Application.Caller.Column
    For Each key In data.keys
        Cells(r, c).Value = key
        Cells(r, c).Offset(1, 0).Resize(1, UBound(data(key)) + 1).Value = Application.WorksheetFunction.Transpose(data(key))
        c = c + 1
    Next key
End Function


Note: This code assumes that you have included a JSON parser module, such as `JsonConverter`, in your VBA project. You can find this tool on GitHub as `VBA-JSON` and follow the instructions there to include it in your VBA environment.