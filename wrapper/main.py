#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
flask server
'''

import os
import json
from flask import Flask, request, Response
from pydash import get as _get

from model.trivial_instance_solver import TrivialInstanceSolver

from utils.handler import Handler
from utils.environment import TE
from utils.service import SERVICE

# Database management
from utils.database import TASKS
from utils.bq import BQ

# Useful request paths
REQ_PATHS = {
    'taskId': '_meta.taskId',
    'warehouseUuid': '_meta.warehouse.uuid',
    'warehouseTag': '_meta.warehouse.tag'
}

APP = Flask(__name__)


@APP.route('/warmup', methods=['GET'])
def warm_up():
    """
    Triggers service warm-up. Prepares some internal variables and reads some data in memory.
    """
    return SERVICE.warm_up()


@APP.route('/pickroute', methods=['POST'])
def optimize_pick_route():
    """
    Pickroute request is opened, passed on to the handler that
    prepares a dict (called solve_dict) that is then passed on to the
    optimizer. After optimization a client_response is returned and
    BigQuery jsons are sent to worker.
    :return: client_response: the response the client (WMS) gets.
    """
    print('/pickroute')
    if not SERVICE.ready():
        return Response('waiting for warm-up', status=503)

    # Read request content
    req = json.loads(request.get_data(as_text=True))
    warehouse_tag = str(_get(req, '_meta.warehouse.tag'))

    if warehouse_tag.lower() == 'demo':
        warehouse_tag = 'DADC'

    # Perform optimization
    handler = Handler(req, SERVICE.wh_dict(), warehouse_tag)
    if len(handler.solve_dict['coords_path_bef_sol']) <= 6:
        TrivialInstanceSolver(handler.solve_dict)
        # brute force search (but still very fast since there are very few nodes in this case)
    else:
        pass
        # INSERT SOLVER with input = handler.solve_dict
    client_response, bq_hist, bq_optim = handler.gen_response(handler.solve_dict)
    # HENCE this returns all finished jsons as in Legacy. As much as this as possible of this
    # functionality should be moved to api

    # Send data to BigQuery
    BQ.pro(bq_hist)
    BQ.pro(bq_optim)

    # Return results
    return client_response


@APP.route('/singlebatch', methods=['POST'])
def optimize_single_batch():
    """
    optimize_single_batch
    :return:
    """
    print('/singlebatch')
    if not SERVICE.ready():
        return Response('waiting for warm-up', status=503)

    # Read request content
    # Source: https://cloud.google.com/tasks/docs/creating-appengine-handlers
    req = json.loads(request.get_data(as_text=True))
    # warehouse_uuid = str(_get(req, '_meta.warehouse.uuid'))
    warehouse_tag = str(_get(req, '_meta.warehouse.tag'))

    if warehouse_tag.lower() == 'demo':
        warehouse_tag = 'DADC'

    # Get task ID
    task_id = _get(req, '_meta.taskId')
    if task_id is None:
        print('Error: Task ID is invalid: ' + str(task_id))
        return json.dumps({
            'error': 'Task ID is invalid: ' + str(task_id)
        })
    if not TASKS.has_task(task_id):
        print('Error: No task with task ID: ' + task_id)
        return json.dumps({
            'error': 'No task with task ID: ' + task_id
        })

    try:
        # Read payload and update tasks table
        data = TASKS.get_payload(task_id)
        TASKS.set_status(task_id, 'running')

        handler = Handler(data, SERVICE.wh_dict(), warehouse_tag)
        # INSERT SOLVER HERE e.g. SingleBatchOptimizer(handler.solve_dict)
        # client_response, _, bq_optim = handler.gen_response(handler.solve_dict, warehouse_uuid)
        client_response, _, bq_optim = handler.gen_response(handler.solve_dict)
        BQ.batching(bq_optim)

        # Update tasks table
        TASKS.set_result(task_id, client_response)
        TASKS.set_status(task_id, 'done')

        # Return results
        return client_response
    except Exception as exc:
        # If optimization failed, put error message in the results field and set status to failed
        TASKS.set_result(task_id, str(exc))
        TASKS.set_status(task_id, 'failed')

        # Return empty string
        print('Error: ' + str(exc))
        return json.dumps({
            'error': str(exc)
        })


if __name__ == '__main__':
    print(os.environ)
    print('starting...')
    PORT = os.environ.get('PORT', 8080)
    if not TE.is_prod():
        SERVICE.warm_up()
        APP.run(host='localhost', port=PORT, debug=True)
