#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
CONFIG
'''

import os

CONFIG = {
    'unix_socket': '',
    'db': '',
    'user': 'DB_USER',
    'passwd': 'DB_PASSWD',
} if os.environ.get('TENSHI_ENVIRONMENT') == 'production' else {
    'host': 'localhost',
    'db': '',
    'user': 'test',
    'passwd': 'test'
}
