#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
Service
'''

import os
import threading
from flask import Response
from .client_storage import get_wh_dict


class Service:
    """
    Service
    """
    STATES = {
        'started': 'STARTED',
        'warm_up': 'WARM_UP',
        'ready': 'READY',
        'failed': 'FAILED'
    }

    """
    Class representing the internal state of the service.

    :class: Service
    """
    def __init__(self):
        """
        Constructor of the service. Sets default values.
        """
        # Warm up state
        self._state = Service.STATES['started']

        # Warehouse dictionary
        self._wh_dict = None

    def _load_wh_dict(self):
        """
        Loads warehouse dictionary as part of the warm up.
        """
        bucket_name = os.environ.get('TENSHI_CLIENT_BUCKET')
        if bucket_name is None:
            print('Missing environment variable TENSHI_CLIENT_BUCKET')
            self._state = Service.STATES['failed']
            return
        self._wh_dict = get_wh_dict(bucket_name)
        if self._wh_dict is None:
            self._state = Service.STATES['failed']
        else:
            self._state = Service.STATES['ready']

    def ready(self):
        """
        Checks if service is ready.

        :return: True if service is ready, false otherwise.
        """
        return self._state == Service.STATES['ready']

    def state(self):
        """
        Returns the current state.
        :return:
        """
        return self._state

    def wh_dict(self):
        """
        Returns the current warehouse dictionary.
        :return: Dictionary containing warehouse information.
        """
        return self._wh_dict

    def warm_up(self):
        """
        Runs warm-up depending on current warm-up state.
        :return: Response corresponding to the warm-up state.
        """
        if self._state == Service.STATES['started']:
            # Service is just starting, go to warm up
            self._state = Service.STATES['warm_up']
            threading.Thread(target=self._load_wh_dict()).start()
            return Response('starting warm-up', status=503)

        if self._state == Service.STATES['warm_up']:
            # Service is warming up
            return Response('running warm-up', status=503)

        if self._state == Service.STATES['ready']:
            # Warm-up is done, service is ready
            return Response('warm-up done', status=200)

        # Warm-pu failed
        return Response('warm-up failed', status=503)


# It's a singleton
SERVICE = Service()
