
Function AlpGet_Account(units As String, account As String, frame As String, taxonomy As String, api_token As String) As Variant
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://127.0.0.1:5000/account?units=" & units & "&account=" & account & "&frame=" & frame & "&taxonomy=" & taxonomy & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send

    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Check if 'data' key exists in the response
    If Not jsonResponse.Exists("data") Then Exit Function

    ' Get the 'data' array from the JSON response
    data = jsonResponse("data")

    ' Check if the cell calling the function is valid
    If IsEmpty(Application.Caller) Then Exit Function

    ' Write the data to Excel starting from the cell where the function is called
    row = Application.Caller.Row + 1
    col = Application.Caller.Column

    ' Write headers
    Cells(Application.Caller.Row, col).Value = "accn"
    Cells(Application.Caller.Row, col + 1).Value = "cik"
    Cells(Application.Caller.Row, col + 2).Value = "end"
    Cells(Application.Caller.Row, col + 3).Value = "entityName"
    Cells(Application.Caller.Row, col + 4).Value = "loc"
    Cells(Application.Caller.Row, col + 5).Value = "start"
    Cells(Application.Caller.Row, col + 6).Value = "val"

    ' Iterate over each item in the 'data' array and write to the sheet
    Dim item As Variant
    For Each item In data
        Cells(row, col).Value = item("accn")
        Cells(row, col + 1).Value = item("cik")
        Cells(row, col + 2).Value = item("end")
        Cells(row, col + 3).Value = item("entityName")
        Cells(row, col + 4).Value = item("loc")
        Cells(row, col + 5).Value = item("start")
        Cells(row, col + 6).Value = item("val")
        row = row + 1
    Next item
End Function
