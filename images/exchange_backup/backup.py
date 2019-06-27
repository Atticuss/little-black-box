import os
import time
import boto3
import logging

from botocore.exceptions import ClientError
from datetime import datetime as dt, timedelta as td

BUCKET_NAME = os.environ["BUCKET_NAME"]
ACCESS_KEY = os.environ["ACCESS_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]

SESSION = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

def s3_backup(parent_dir, filename):
    s3 = SESSION.resource("s3")

    key = "%s/%s" % (parent_dir, filename)
    full_path = os.path.join("/data", parent_dir, filename)

    retry = True
    attempts = 0
    while retry and attempts < 5:
        try:
            s3.Bucket(BUCKET_NAME).upload_file(full_path, key)
            retry = False
        except ClientError as ce:
            logging.error("boto3 error: %s" % ce.response['Error'])
            time.sleep(1)
        except Exception as e:
            logging.error("non-boto3 error: %s" % e)
            time.sleep(1)
        
        attempts += 1

    if retry:
        logging.error("Unable to backup, attempted %s times" % attempts)
    else:
        logging.info("Successfully backed up: %s" % key)

if __name__ == "__main__":
    ts = (dt.utcnow() - td(days=1)).strftime("%d-%m-%y")
    hdf_fname = "%s.hdf" % ts

    filenames = os.listdir("/data")
    for filename in filenames:
        if os.path.isdir(os.path.join("/data", filename)):
            s3_backup(filename, hdf_fname)