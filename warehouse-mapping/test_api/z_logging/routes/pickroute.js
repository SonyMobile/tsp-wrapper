/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { PROJECT_ID, DATA_SETS, TABLES } = require('../src/bq/tables');
const router = require('express').Router();
const Logs = require('../src/bq/logs');
const Raw = require('../src/bq/raw');
const PickRoute = require('../src/bq/pickroute');
const Errors = require('../src/errors');

/**
 * Reads data from request body and posts it to the corresponding table in BigQuery.
 *
 * @method post
 * @param {string} dataSetId ID of the current data set to use.
 * @param {Object} req The request object.
 * @param {Object} res The response object.
 * @returns {Promise<*>} Empty promise.
 */
async function post(dataSetId, req, res) {
    // TODO Get rid of PubSub, use endpoint directly.
    // Try to read message from PubSub
    let data = null;
    try {
        data = Buffer.from(req.body.message.data, 'base64').toString('utf-8');
    } catch (e) {
        // Data is sent via Postman
        try {
            data = JSON.stringify(JSON.parse(req.body.message).data);
        } catch (e) {
            return res.status(500).json({error: Errors.UNKNOWN_SOURCE});
        }
    }

    // Parse JSON content
    let json = null;
    try {
        json = JSON.parse(data);
    } catch (e) {
        Logs.insert(dataSetId, TABLES.PICK_ROUTE, null, e.message);
        return res.status(500).json({error: Errors.INVALID_JSON(e.message)});
    }

    // Extract job ID
    let jobId = json.jobId;
    if (typeof jobId === 'undefined') {
        Logs.insert(dataSetId, TABLES.PICK_ROUTE, null, 'Missing jobId.');
        return res.status(500).json({error: Errors.MISSING_JOB_ID});
    }

    // Check if data is already in table
    if (await PickRoute.count(DATA_SETS.TEST, jobId) > 0) {
        let m = 'Pick run already in BQ.';
        console.log(m);
        return res.status(200).json({message: m});
    }

    // Insert pick route entry
    PickRoute.insert(dataSetId, json).then(() => {
        // If successful, insert JSON to raw table as well
        Raw.insert(dataSetId, jobId, data).then(() => {
            console.log('JSON inserted in raw table.');
        }).catch(e => {
            console.log(`Could not insert raw JSON: ${e}.`);
        });

        let m = `Pick route data successfully inserted to ${PROJECT_ID}.${dataSetId}.${TABLES.PICK_ROUTE}.`;
        console.error(m);
        Logs.insert(dataSetId, TABLES.PICK_ROUTE, jobId);
        return res.status(200).json({message: m});
    }).catch(e => {
        console.log(`Could not insert data. ${e.message}.`);
        Logs.insert(dataSetId, TABLES.PICK_ROUTE, jobId, e.message);
        return res.status(500).json({error: e});
    });
}

/**
 * Posts a JSON to the pick run optimization table in the test data set. The body must have a message.data path
 * containing the JSON. This route is always open.
 *
 * @name POST /test/pickroute
 */
router.post('/test/pickroute', async (req, res) => {
    await post(DATA_SETS.TEST, req, res);
});

/**
 * Posts a JSON to the pick run optimization table in the stage data set. The body must have a message.data path
 * containing the JSON. This route is always open.
 *
 * @name POST /stage/pickroute
 */
router.post('/stage/pickroute', async (req, res) => {
    await post(DATA_SETS.STAGE, req, res);
});

/**
 * Posts a JSON to the pick run optimization table in the prod data set. The body must have a message.data path
 * containing the JSON. This route is only open in production mode.
 *
 * @name POST /prod/pickroute
 */
router.post('/prod/pickroute', async (req, res) => {
    if (process.env.NODE_ENV === 'production') {
        await post(DATA_SETS.PROD, req, res);
    } else {
        res.status(500).send('/prod/pickroute is only open in production mode.');
    }
});

module.exports = router;
