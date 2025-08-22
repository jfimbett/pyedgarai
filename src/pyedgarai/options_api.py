rapipdf_html_string = """
<!doctype html>
<html>
<head>
    <script src="https://unpkg.com/rapipdf/dist/rapipdf-min.js"></script>
</head>
<body>
<rapi-pdf
        style="width:700px; height:40px; font-size:18px;"
        spec-url="{{api_doc_url}}"
        button-bg="#b44646"
></rapi-pdf>
</body>
</html>
"""