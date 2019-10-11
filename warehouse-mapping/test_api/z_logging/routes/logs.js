/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const router = require('express').Router();
const { DATA_SETS } = require('../src/bq/tables');
const Logs = require('../src/bq/logs');

/**
 * Returns the latest logs in the test data set. This route is always open.
 *
 * @name GET /test/logs
 * @param {number} limit Number of log entries to return.
 * @param {number} offset Number of log entries to skip.
 * @returns {Object[]} JSON array of the latest log entries sorted by time in descending order.
 */
router.get('/test/logs', async (req, res) => {
    let results = await Logs.select(DATA_SETS.TEST, req.query.limit, req.query.offset);
    res.status(200).json(results[0]);
});

/**
 * Returns the latest logs in the stage data set. This route is always open.
 *
 * @name GET /stage/logs
 * @param {number} limit Number of log entries to return.
 * @param {number} offset Number of log entries to skip.
 * @returns {Object[]} JSON array of the latest log entries sorted by time in descending order.
 */
router.get('/stage/logs', async (req, res) => {
    let results = await Logs.select(DATA_SETS.STAGE, req.query.limit, req.query.offset);
    res.status(200).json(results[0]);
});

/**
 * Returns the latest logs in the prod data set. It is only open when in production mode. If accessed in development
 * mode, it returns status 500.
 *
 * @name GET /prod/logs
 * @param {number} limit Number of log entries to return.
 * @param {number} offset Number of log entries to skip.
 * @returns {Object[]} JSON array of the latest log entries sorted by time in descending order.
 */
router.get('/prod/logs', async (req, res) => {
    if (process.env.NODE_ENV === 'production') {
        // Run select query on logs
        let results = await Logs.select(DATA_SETS.PROD, req.query.limit, req.query.offset);
        res.status(200).json(results[0]);
    } else {
        res.status(500).send('/prod/logs is only open in production mode.');
    }
});

module.exports = router;
