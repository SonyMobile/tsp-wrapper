#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
Environment
'''

import os


class Environment:
    """
    Convenience class to query current  environment.

    :class: Environment
    """
    def __init__(self):
        """
        Constructor, sets environment.
        """
        self._env = os.environ.get('ENVIRONMENT')

    def get(self):
        """
        Returns the current  environment.

        :return: The current  environment.
        """
        return self._env

    def is_prod(self):
        """
        Checks if current  environment is 'production'.

        :return: True if  environment is 'production', false otherwise.
        """
        return self._env == 'production'


# Singleton
TE = Environment()
