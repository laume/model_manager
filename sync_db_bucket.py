import sqlite3
import boto3
import sys
import pandas as pd
from credentials import *

s3 = boto3.resource('s3')
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

def syncer(s3, bucket, conn, cur):
    """add this to cron to sync database with cloud"""
    # Check models in cloud
    try:
        models_in_cloud = [object.key for object in s3.Bucket(bucket).objects.all()]
        print(models_in_cloud)
    except:
        # TODO add logger
        # print('Can\'t list bucket items... Try again!')
        sys.exit()

    # Get models from database:
    df = pd.read_sql('select name, version from model_info where available=1;', conn)
    if not df.empty:
        print('You have following models in cloud: \n', df)
    else:
        print('You have no saved models at the moment')
    # TODO finish sync function


syncer(s3, BUCKET_NAME)
