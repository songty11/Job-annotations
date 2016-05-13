from bottle import subprocess
import json
import os
import boto3
import time
import botocore
import os

# Connect to SQS and get the message queue
# Poll the message queue in a loop 
sqs = boto3.resource('sqs')
s3 = boto3.resource('s3')
queue = sqs.get_queue_by_name(QueueName='songty_job_requests')
while True:

    # long polling
    # https://github.com/boto/boto3-sample/blob/master/transcoder.py
    messages = queue.receive_messages(MaxNumberOfMessages=10,WaitTimeSeconds=20)
    if len(messages) > 0:
        for message in messages:
            # http://boto3.readthedocs.io/en/latest/reference/services/sqs.html#SQS.Message.body
            data = json.loads(message.body)
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
            message.delete()