import sqlite3
import boto3
from send_models import upload_to_cloud, remove_from_cloud, list_bucket_items, download_model
from credentials import *
from utils import simple_input

s3 = boto3.resource('s3')

def model_manager():
    """"This function is used as user interface for command line"""
    print('Here you can download, upload, delete or list models existing in bucket.\n')
    msg_model_name = 'Please enter model name\n'
    msg_folder = 'Provide folder where to download\n'
    msg_model_path = 'Provide model path\n'
    msg_version = 'Provide model version\n'
    message = 'Choose the option you want to do: \ndownload: d, upload: u, list l, delete: r.\n'
    options = {'d', 'u', 'l', 'r'}
    action = simple_input(message, options)
    if action == 'd':
        model_name = str(input(msg_model_name))
        models_folder = str(input(msg_folder))
        download_model(BUCKET_NAME, model_name, models_folder)
    elif action == 'u':
        model_path = str(input(msg_model_path))
        version = str(input(msg_version))
        model_name = str(input(msg_model_name))
        upload_to_cloud(BUCKET_NAME, model_path, version, model_name)
    elif action == 'l':
        list_bucket_items(BUCKET_NAME)
    elif action == 'r':
        model_name = str(input(msg_model_name))
        remove_from_cloud(BUCKET_NAME, model_name)


if __name__ == '__main__':
    model_manager()