from bottle import get,template,request,post,run,route,response,subprocess
import uuid
import json
import boto3
import datetime
import hmac
import hashlib
import base64
import botocore.session as botosession
import urllib2
import time

sqs = boto3.resource('sqs')

# upload file using form
@get('/upload')
def upload_file_to_s3():
    # redirect_url = "http://songty.ucmpcs.org:8888/send_annotation_request"
    redirect_url = str(request.url) + "/send_annotation_request"
    print redirect_url
    time = datetime.timedelta(days = 1) + datetime.datetime.today();
    # define S3 policy document 
    policy = {"expiration":time.strftime('%Y-%m-%dT%H:%M:%S.000Z'), 
            "conditions": 
            [{"bucket":"gas-inputs"},
            {"acl": "private"},
            ["starts-with", "$key", "songty/"],
            ["starts-with", "$success_action_redirect",redirect_url],
            ]
            }

   #https://docs.python.org/2/library/base64.html
    Policy_Code = base64.b64encode(str(policy)).encode('utf8')

    s3_key = str(uuid.uuid4())

    session = botosession.get_session()
    credentials = session.get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key

    #https://docs.python.org/2/library/hmac.html
    my_hmac = hmac.new(secret_key.encode(),Policy_Code,hashlib.sha1)
    digest = my_hmac.digest()
    signature = base64.b64encode(digest)
    tpl = template("upload.tpl",bucket_name = "gas-inputs",policy = Policy_Code,aws_key = access_key,signature = signature,redirect = redirect_url,s3_key = s3_key)
    return tpl

@get('/upload/send_annotation_request')
def send_annotation_request():
    formdata = request.query
    bucket = formdata["bucket"]
    key = formdata["key"]

    file_name = key.split("/")[-1]
    job_id = file_name.split("~")[0]

    data = {"job_id": str(job_id),
            "username": "songty",
            "s3_inputs_bucket": "gas-inputs",
            "s3_key_input_files": key,
            "input_file_name": file_name.split("~")[1],
            "submit_time": int(time.time()),
            "job_status": "PENDING"
            }

    dynamodb = boto3.resource('dynamodb')
    ann_table = dynamodb.Table('songty_annotations')
    ann_table.put_item(Item=data)
    
    #http://boto3.readthedocs.io/en/latest/reference/services/sqs.html#queue
    queue = sqs.get_queue_by_name(QueueName='songty_job_requests')
    queue.send_message(MessageBody=json.dumps(data))

    return_data = {'id': job_id, 'file_name': file_name}
    return json.dumps({'code': response.status, 'data': return_data})

run(host='0.0.0.0',port=8888,debug=True)