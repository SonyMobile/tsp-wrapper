#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
Tasks
'''
import os
import json
import pymysql
from .db_config import CONFIG



class Tasks:
    """
    Tasks
    """

    STATUSES = {
        'waiting': 'waiting',
        'running': 'running',
        'done': 'done',
        'failed': 'failed',
    }

    """
    Singleton class implementing task table related operations.

    :class: Tasks
    """
    def __init__(self):
        """
        Constructor for the Tasks class. Sets up connection and cursor to the SQL database.
        """
        if os.environ.get('TENSHI_ENVIRONMENT') == 'production':
            self._db = pymysql.connect(unix_socket=CONFIG['unix_socket'],
                                       db=CONFIG['db'],
                                       user=CONFIG['user'],
                                       passwd=CONFIG['passwd'])
        else:
            self._db = pymysql.connect(host=CONFIG['host'],
                                       db=CONFIG['db'],
                                       user=CONFIG['user'],
                                       passwd=CONFIG['passwd'])
        self._cursor = self._db.cursor()

    def has_task(self, task_id):
        """
        Checks if task exists for a specific task ID.

        :param task_id: Task ID to check existence for.
        :return: True if task exists, false otherwise.
        """
        self._cursor.execute('SELECT id FROM tasks WHERE uuid = %s', (task_id, ))
        return len(self._cursor.fetchall()) > 0

    def insert_task(self, task):
        """
        insert_task
        :param task:
        :return:
        """
        self._cursor.execute('''INSERT INTO tasks (uuid, type, warehouse_id, payload, status)
                                VALUES (%s, %s, %s, %s, 'waiting')''',
                             (task['uuid'], task['type'], task['warehouse_id'], task['payload']))
        self._db.commit()

    def get_payload(self, task_id):
        """
        Retrieves the payload for a specific task. If the task ID
        belongs to zero or multiple tasks, it raises an exception.

        :param task_id: Task ID to collect payload for.
        :raises: KeyError if the task ID belongs to zero or multiple tasks.
        :return: The payload to the task identified by the task ID as a dictionary.
        """
        self._cursor.execute('SELECT payload FROM tasks WHERE uuid = %s', (task_id,))
        task_payloads = [row for row in self._cursor]

        # Check if there are zero or multiple tasks
        if not task_payloads:
            raise KeyError('No task with task ID: ' + task_id)
        if len(task_payloads) > 1:
            raise KeyError('Multiple tasks with task ID: ' + task_id)

        # Return payload
        return json.loads(task_payloads[0][0])

    def set_status(self, task_id, status):
        """
        Updates the task status for a specific task.

        :param task_id: Task ID to update status for.
        :param status: The new status to update task to.
        :raises: ValueError if status is invalid.
        :raises: KeyError if there is no task with the specified task ID.
        """
        # Check if status is valid
        if status not in Tasks.STATUSES:
            raise ValueError('Invalid status: ' + status)

        # Check if task ID exists
        if not self.has_task(task_id):
            raise KeyError('No task with task ID: ' + task_id)

        # Check if task exists
        self._cursor.execute('UPDATE tasks SET status = %s WHERE uuid = %s', (status, task_id))
        self._db.commit()
        print('Tasks: status is updated to {} for task {}'.format(status, task_id))

    def set_result(self, task_id, result):
        """
        Updates the task status for a specific task.

        :param task_id: Task ID to update status for.
        :param result: The result as a stringified JSON.
        :raises: ValueError if status is invalid.
        :raises: KeyError if there is no task with the specified task ID.
        """
        # Check if status is valid
        if not self.has_task(task_id):
            raise KeyError('No task with task ID: ' + task_id)

        # Check if task exists
        self._cursor.execute('UPDATE tasks SET result = %s WHERE uuid = %s', (result, task_id))
        self._db.commit()


# Tasks is a singleton
TASKS = Tasks()
