/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { isEmpty } = require('lodash');
const router = require('express').Router();
const { createSingleBatchTask } = require('../src/tasks.js');
const { getTask } = require('../src/db.js');
const Errors = require('../src/errors');


/**
 * Checks for request errors.
 *
 * @method requestErrors
 * @param {Object} data The request data.
 * @returns {(Object|null)} Object describing the error if any, null otherwise.
 */
function requestErrors(data) {
    if (typeof data === 'undefined' || isEmpty(data)) {
        return Errors.EMPTY_REQUEST;
    }
    return null;
}

/**
 * POST /v1/optimize/singlebatch
 */
router.post('/', async (req, res) => {
    // Get warehouse (set by auth.js)
    const warehouse = req._warehouseData;

    // Read request data and validate
    const data = req.body;
    let reqError = requestErrors(data);
    if (reqError !== null) {
        return res.status(400).json({ error: reqError });
    }

    // Create task, retrieve UUID
    const taskUuid = await createSingleBatchTask(warehouse, data);

    // Return location of future result
    const taskUrl = `${req.protocol}://${req.get('host')}${req.originalUrl}/${taskUuid}`;
    res.set('Location', taskUrl);
    return res.status(202).json({
        accepted: true,
        taskId: taskUuid,
        url: taskUrl
    });
});

/**
 * GET  /v1/optimize/singlebatch
 *
 * This route is added to support the missing task ID case (otherwise the would return 404).
 */
router.get('/', (req, res) => {
    return res.status(400).json({ error: Errors.MISSING_TASK_ID });
});

/**
 * GET  /v1/optimize/singlebatch/:uuid
 */
router.get('/:uuid', async (req, res) => {
    // Get warehouse (set by auth.js)
    const warehouse = req._warehouseData;

    // Read task UUID, retrieve corresponding task
    const taskUuid = req.params.uuid;
    const task = await getTask(taskUuid);

    // Check if task exists
    if (typeof task === 'undefined') {
        return res.status(400).json({ error: Errors.INVALID_TASK_ID(taskUuid) });
    }

    // Check if task corresponds to current warehouse
    if (task.warehouse_id !== warehouse.id) {
        return res.status(403).json({ error: Errors.UNAUTHORIZED_WAREHOUSE(warehouse.uuid) });
    }

    // Otherwise, respond according to current task status
    switch (task.status) {
        // TODO Move statuses to constants
        case 'waiting':
        case 'running':
            return res.status(202).json({
                accepted: true,
                status: task.status
            });
        case 'done':
            return res.status(200).json(JSON.parse(task.result));
        case 'failed':
        default:
            return res.status(418).json({ error: Errors.TASK_FAILED(task.result) });
    }
});

module.exports = router;
