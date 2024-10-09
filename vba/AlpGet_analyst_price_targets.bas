
Function AlpGet_analyst_price_targets(ticker As String, api_token As String)
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = "http://127.0.0.1:5000/analyst_price_targets?ticker=" & ticker & "&api_token=" & api_token
    
    http.Open "GET", url, False
    http.setRequestHeader "accept", "application/json"
    http.send
    
    Dim response As String
    response = http.responseText
    
    ' Parse the JSON response
    Dim json As Object
    Set json = JsonConverter.ParseJson(response)
    
    Dim data As Variant
    data = json("data")
    
    Dim currentCell As Range
    Set currentCell = Application.Caller

    currentCell.Value = "Current"
    currentCell.Offset(0, 1).Value = data("current")
    
    currentCell.Offset(1, 0).Value = "High"
    currentCell.Offset(1, 1).Value = data("high")
    
    currentCell.Offset(2, 0).Value = "Low"
    currentCell.Offset(2, 1).Value = data("low")
    
    currentCell.Offset(3, 0).Value = "Mean"
    currentCell.Offset(3, 1).Value = data("mean")
    
    currentCell.Offset(4, 0).Value = "Median"
    currentCell.Offset(4, 1).Value = data("median")
    
End Function


Note: This code assumes you have already included a JSON parser module (such as `JsonConverter`) to parse the JSON response. If not, you will need to add one to handle the JSON parsing in VBA.