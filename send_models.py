import boto3
import sqlite3
import pandas as pd
import os
import sys
import credentials
from utils import input_number, confirm_input


s3 = boto3.resource('s3')
bucket = credentials.BUCKET_NAME
database = credentials.DATABASE
models_folder = credentials.MODEL_STORAGE

# Check if database exists, if not - create new
db_exists = os.path.isfile(database)
if not db_exists:
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    # create needed tables
    model_info = 'Create Table model_info (id Int, name Varchar, version Varchar, local_storage Varchar, available Int);'
    cur.execute(model_info)
    conn.commit()


# conn = sqlite3.connect(database)
# cur = conn.cursor()


# TODO check if works with added path and upload model with database id
def upload_to_cloud(bucket, model_path, version, model_name=None):
    s3 = boto3.resource('s3')
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    if model_name is None:
        model_name = model_path.split('/')[-1]
    # add model data to database
    try:
        cur.execute("Insert Into model_info (name, version, local_storage, available) Values ('{}', '{}', '{}', 1);"
                    .format(model_name, version, model_path))
        model_id = cur.lastrowid
    except:
        print('Problems with saving model data to database... Try again!')
        sys.exit(1)

    # send model to cloud
    try:
        data = open(model_path, 'rb')
        s3.Bucket(bucket).put_object(Key='model_{}_{}'.format(model_name, model_id), Body=data)
    except:
        print('Problems with uploading model to cloud... Try again!')
        sys.exit(1)

    conn.commit()
    print('Your model uploaded successfully!')

# upload_to_cloud(s3, bucket, cur, 'test_file.txt', 'v2', 'third')


def remove_from_cloud(bucket, model_name):
    s3 = boto3.resource('s3')
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    # change model availability in database
    try:
        cur.execute("Select rowid, name, version from model_info where name='{}' and available=1;"
                    .format(model_name))
        result = cur.fetchall()
        if result:
            if len(result) == 1:
                model_id = result[0][0]
            else:
                print('You have more than one model with such a name:')
                print([res for res in result])
                model_id = input_number('Input model id you want to delete (Enter 0 to Cancel):\n')
            cur.execute("Update model_info set available=0 where rowid={}".format(model_id))
        else:
            print('You don\'t have model with provided name, exiting without any changes')
            sys.exit()
    except (sqlite3.DatabaseError, sqlite3.OperationalError, sqlite3.ProgrammingError):
        print('Problems with updating model status in database... Try again!')
        sys.exit(1)

    # delete model from cloud:
    try:
        model_to_delete = 'model_{}_{}'.format(model_name, model_id)
        s3.Object(bucket_name=bucket, key=model_to_delete).delete()
    except:
        print('Problems with deleting model from cloud... Try again!')
        sys.exit()

    conn.commit()
    print('Your model deleted successfully!')

# remove_from_cloud(s3, bucket, conn, cur, 'third')


def list_bucket_items(bucket):
    s3 = boto3.resource('s3')
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    # TODO do synchronization between cloud and local storage
    df = pd.read_sql('select name, version, local_storage from model_info where available=1;', conn)
    if not df.empty:
        print('You have following models in cloud: \n', df)
    else:
        print('You have no saved models at the moment')
        # TODO check with data in bucket
    # try:
    #     for object in s3.Bucket(bucket).objects.all():
    #         print(object.key)
    # except:
    #     print('Can\'t list bucket items... Try again!')
    #     sys.exit()


# list_bucket_items(s3, bucket, conn)


# TODO check why sys exit not works
def download_model(bucket, model_name, models_folder):
    s3 = boto3.resource('s3')
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    # check model availability in database
    try:
        cur.execute("Select rowid, name, version from model_info where name='{}' and available=1;"
                    .format(model_name))
        result = cur.fetchall()
        if result:
            if len(result) == 1:
                model_id = result[0][0]
            else:
                print('You have more than one model with such a name:')
                print([res for res in result])
                model_id = input_number('Input model id you want to download (Enter 0 to Cancel):\n')
        else:
            print('You don\'t have model with provided name, exiting without any changes')
            sys.exit()
    except (sqlite3.DatabaseError, sqlite3.OperationalError, sqlite3.ProgrammingError):
        print('Problems while checking model info in database... Try again!')
        sys.exit(1)

    # Check if directory exists
    if not os.path.isdir(models_folder):
        print('New directory for models has been created.')
        os.makedirs(models_folder)
    else:
        model = os.path.isfile('{}{}'.format(models_folder, model_name))
        if model:
            confirmation = confirm_input('Model with such name exists, do you want to replace (y/n)?\n')
            if not confirmation:
                print('Exiting without changes...')
                sys.exit()

    # download model from cloud:
    try:
        model_to_download = 'model_{}_{}'.format(model_name, model_id)
        print(model_to_download)
        s3.Object(bucket_name=bucket, key=model_to_download).download_file('{}/{}'.format(models_folder, model_name))
    except:
        print('Problems with model download from cloud... Try again!')
        sys.exit()

    print('Your model downloaded successfully!')


# download_model(bucket, 'third', 'here')

# conn.close()
