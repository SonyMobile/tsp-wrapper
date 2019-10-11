#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
get_node_from_keydict
'''

def get_node_from_keydict(section, rack, tier, keydict_kc):

    """
    get_node_from_keydict
    :param section:
    :param rack:
    :param tier:
    :param keydict_kc:
    :return:
    """

    key = section + '_' + rack + '_' + tier
    idx = keydict_kc[key]
    return idx
