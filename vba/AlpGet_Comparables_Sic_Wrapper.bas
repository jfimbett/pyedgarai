
Function AlpGet_Comparables_Sic_Wrapper(cik As String, api_token As String) As String
    ' Add an error handler
    On Error GoTo ErrorHandler
    Dim url As String
    Dim xmlhttp As Object
    Dim jsonResponse As Object
    Dim data As Variant
    Dim row As Long
    Dim col As Long

    ' Set the endpoint URL
    url = "http://localhost:5000/comparables_sic?cik=" & cik & "&api_token=" & api_token

    ' Create the XMLHTTP object
    Set xmlhttp = CreateObject("MSXML2.XMLHTTP")

    ' Set up the request
    xmlhttp.Open "GET", url, False
    xmlhttp.setRequestHeader "Accept", "application/json"

    ' Send the request
    xmlhttp.Send
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(xmlhttp.responseText)

    ' Assuming the response is a dictionary or array of dictionaries
    row = ActiveCell.Row
    col = ActiveCell.Column
    
    Dim hasKey As Boolean
    hasKey = False

    ' Check whether the response is dictionary or array of dictionaries
    If Not (TypeName(jsonResponse) = "Dictionary" Or TypeName(jsonResponse) = "Collection") Then GoTo ExitFunction

    ' If the response is collection (array of dictionaries)
    If TypeName(jsonResponse) = "Collection" Then
        For Each data In jsonResponse
            If Not hasKey Then
                ' Write headers
                Dim key As Variant
                Dim headerCol As Long
                headerCol = col
                For Each key In data.Keys
                    Cells(row, headerCol).Value = key
                    headerCol = headerCol + 1
                Next key
                hasKey = True
                row = row + 1
            End If
            ' Write values
            Dim value As Variant
            Dim valueCol As Long
            valueCol = col
            For Each value In data.Items
                Cells(row, valueCol).Value = value
                valueCol = valueCol + 1
            Next value
            row = row + 1
        Next data
    ElseIf TypeName(jsonResponse) = "Dictionary" Then
        ' If the response is a single dictionary
        Dim responseKey As Variant
        Dim responseCol As Long

        responseCol = col
        For Each responseKey In jsonResponse.Keys
            ' Write headers
            Cells(row, responseCol).Value = responseKey
            responseCol = responseCol + 1
        Next responseKey
        row = row + 1
        DataRow = row
        responseCol = col
        For Each responseKey In jsonResponse.Keys
            ' Write row data
            Cells(DataRow, responseCol).Value = jsonResponse(responseKey)
            responseCol = responseCol + 1
        Next responseKey
    End If

ExitFunction:
    AlpGet_Comparables_Sic_Wrapper = "cik=" & cik & "&api_token=" & api_token
    Exit Function
    
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description & " " & Erl
    Exit Function
End Function

Function AlpGet_Comparables_Sic(cik As String, api_token As String) As String
    Dim result As String
    result = Evaluate("AlpGet_Comparables_Sic_Wrapper(""" & cik & """,""" & api_token & """)")
    AlpGet_Comparables_Sic = result
End Function
