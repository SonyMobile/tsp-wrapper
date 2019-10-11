#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
get_wh_dict() is the function that conducts the warmup.
'''


import os
import pickle
from google.cloud import storage


def get_wh_dict(bucket_name):
    """
    Example of warmup (loading warehouse specific files into RAM)
    get_wh_dict
    :param bucket_name:
    :return:
    """
    data_files = [
        'allcoords',
        'keydict',
        'distmat',
        'spnodeslist',
        'startendndarray'
    ]

    file_map = {}
    try:
        # Map up files. Download files if in production
        client_data_dir = 'client-data'
        bucket_data_path = 'optimizer-data'
        data_path = '{}/{}'.format(os.getcwd(), client_data_dir)

        if os.environ.get('TENSHI_ENVIRONMENT') == 'production':
            print('client data path: ' + data_path)
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            for file_name in data_files:
                file = '{}/{}'.format(bucket_data_path, file_name)
                print('Downloading {} from {}'.format(file, bucket_name))
                blob = bucket.blob(file)
                target_file = '{}/{}'.format(client_data_dir, file_name)
                blob.download_to_filename(target_file)
        else:
            # print('Using dict data from local folder {}'.format(bucket_name))
            data_path = bucket_name

        # Pickle data from files to file_map
        for file_name in data_files:
            file = '{}/{}'.format(data_path, file_name)
            print('Loading {}'.format(file))
            with open(file, 'rb') as handle:
                file_map[file] = {}
                file_map[file] = pickle.load(handle, encoding='latin1')
                print('Loaded {} : {}'.format(file, file_map[file]))

    except Exception as exc:
        print('Error {}'.format(exc))
        # print('Failed to create dictionary from data files: ' + e)
        file_map = None

    return file_map
