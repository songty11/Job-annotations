# Copyright (C) 2011-2016 Vas Vasiliadis
# University of Chicago
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'
import boto3
import botocore
import sys
import time
import driver
import os

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

# A rudimentary timer for coarse-grained profiling
class Timer(object):
        def __init__(self, verbose=False):
                self.verbose = verbose

        def __enter__(self):
                self.start = time.time()
                return self

        def __exit__(self, *args):
                self.end = time.time()
                self.secs = self.end - self.start
                self.msecs = self.secs * 1000  # millisecs
                if self.verbose:
                        print "Elapsed time: %f ms" % self.msecs

if __name__ == '__main__':
        # Call the AnnTools pipeline
        if len(sys.argv) > 1:
                input_file_name = sys.argv[1]
                with Timer() as t:
                        driver.run(input_file_name, 'vcf')
                print "Total runtime: %s seconds" % t.secs
                log_path = input_file_name + ".count.log"
                log_name = input_file_name.split('/')[1] + ".count.log"
                res_path = input_file_name.split('.')[0] + ".annot.vcf"
                res_name = input_file_name.split('.')[0].split('/')[1] + ".annot.vcf"

                #http://boto3.readthedocs.org/en/latest/reference/services/s3.html#S3.Client.upload_file
                s3.meta.client.upload_file(log_path, 'gas-results', "songty/" + log_name)
                s3.meta.client.upload_file(res_path, 'gas-results', "songty/" + res_name)
                
                #https://docs.python.org/2/library/os.html#os.remove
                os.remove(input_file_name)
                os.remove(log_path)
                os.remove(res_path)

                #https://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html?highlight=dynamodb#DynamoDB.Client.update_item
                table = dynamodb.Table('songty_annotations')
                table.update_item(Key={"job_id": input_file_name.split("~")[0].split('/')[-1]}, 
                                UpdateExpression="set s3_results_bucket = :resB,\
                                                s3_key_result_file = :resF,\
                                                s3_key_log_file = :logF,\
                                                complete_time = :cT,\
                                                job_status = :jobS",
                                ExpressionAttributeValues={
                                    ":resB": "gas-results",
                                    ":resF": "songty/" + res_path + ".annot.vcf",
                                    ":logF": "songty/" + res_name + ".vcf.count.log",
                                    ":cT": int(time.time()),
                                    ":jobS": "COMPLETE"
                                })

        else:
                print 'A valid .vcf file must be provided as input to this program.'