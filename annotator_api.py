from bottle import get,request,post,run,route,response,subprocess
import uuid
import json
import boto3
import botocore
import os

s3 = boto3.resource('s3')

@post('/annotator')
def annotate():
    # extract job parameters from the request body
    data = request.json
    job_id = data["job_id"]
    bucket_name = data["s3_inputs_bucket"]
    key = data["s3_key_input_files"]
    file_name_withpath = 'jobs/' + key.split('/')[-1]
    if not os.path.exists('jobs/'):
            os.makedirs('jobs/')

    # Get the input file S3 object and copy it to a local file
    s3.Bucket(bucket_name).download_file(key, file_name_withpath)

    # Launch annotation job as a background process
    cmd = "python run.py " + file_name_withpath
    subprocess.Popen(cmd.split())
    # Return response to notify user of successful submission
    data = {'id': job_id, 'input_file': key}
    return json.dumps({'code': response.status, 'data': data})

run(host='0.0.0.0', port=8888, debug=True)
                                     