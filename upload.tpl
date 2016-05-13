<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
  <h1>Annotate VCF File</h1>
  <form id="upload_form" action="https://{{bucket_name}}.s3.amazonaws.com/" method="post" enctype="multipart/form-data">   
    <input type="hidden"  name="key" value="songty/{{s3_key}}~${filename}" /><br />
    <input type="hidden" name="AWSAccessKeyId" value="{{aws_key}}">
    <input type="hidden" name="success_action_redirect" value="{{redirect}}" />
    <input type="hidden" name="Policy" value='{{policy}}' />
    <input type="hidden" name="Signature" value="{{signature}}" />
    <input type="hidden" name="acl" value="private" />
    <br>VCF Input File: <input id="upload_file" type="file" name="file" /><br>

    <br><input type="submit" value="Upload Annotator" /></br>
  </form>
</body>
</html>