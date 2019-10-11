#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
BigQuery uploads
'''

import base64
from threading import Thread
from os import environ
import requests
from utils.environment import TE

class BQ:
    """
    Class implementing BigQuery uploads.

    :class: BQ
    """
    BASE_URL = 'https://.../{}/{}'
    print(environ.get('TENSHI_WORKER_URL'))

    def __init__(self):
        """
        Constructor. Sets data set based on current  environment.
        """
        # self._data_set = 'test'
        self._data_set = 'stage'
        if TE.is_prod():
            self._data_set = 'stage'

    @staticmethod
    def _wrap_data(data_str):
        """
        Wraps data to be accepted by the worker

        :param data_str: Data to send as a stringified JSON.
        :return: The wrapped dictionary.
        """

        return {
            'message': {
                'data': base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
            }
        }

    @staticmethod
    def _post(url, data_str):
        """
        Posts data to the worker.

        :param url: URL to post data to.
        :param data_str: The data to post as a stringified JSON.
        """
        response = requests.post(url, json=BQ._wrap_data(data_str))
        print(response.content)

    @staticmethod
    def _async_post(url, data_str):
        """
        Posts data to the worker asynchronously.

        :param url: URL to post data to.
        :param data_str: The data to post as a stringified JSON.
        :return:
        """
        Thread(target=BQ._post(url, data_str)).start()

    def pro(self, data_str):
        """
        Sends data to the pick route optimization table in BQ.

        :param data_str: Payload to send as a stringified JSON.
        """
        print('Sending data to /pro')
        BQ._async_post((BQ.BASE_URL.format(self._data_set, 'pickroute')), data_str)

    def batching(self, data_str):
        """
        Sends data to the batching table in BQ.

        :param data_str: Payload to send as a stringified JSON.
        :return:
        """
        print('Sending data to /batching')
        BQ._async_post(BQ.BASE_URL.format(self._data_set, 'singlebatch'), data_str)


# It's a singleton, of course :)
BQ = BQ()
