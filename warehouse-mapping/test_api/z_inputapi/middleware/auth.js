/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const config = require('../src/config');
const { getWarehousesByApiKey } = require('../src/db');
const { X_API_KEY } = require('../src/header');
const Errors = require('../src/errors');
const get = require('lodash.get');

/**
 * Module implementing the authorization of a warehouse. Warehouses are authorized by their API keys.
 *
 * @method authorize
 * @param {Object} req The request object.
 * @param {Object} res The response object.
 * @param {Function} next Function that goes to the next middleware.
 */
module.exports = async function (req, res, next) {
    // Read API key from header or request data
    const apiKey = req.get(X_API_KEY) || get(req.body, 'requestData.apiKey');
    if (typeof apiKey === 'undefined') {
        return res.status(401).json({ error: Errors.MISSING_API_KEY });
    }

    // Find warehouse by its API key and check for errors
    const rows = await getWarehousesByApiKey(apiKey);
    if (rows.length === 0) {
        return res.status(401).json({ error: Errors.INVALID_API_KEY });
    } else if (rows.length > 1) {
        return res.status(500).json({ error: Errors.CONFLICTING_API_KEYS });
    }

    // Set warehouse
    const row = rows[0];
    row.apiKey = apiKey;

    // Add URL to legacy endpoints
    row.paths = {
        optimizerUrl: config.endpoints.getOptimizerUrl(row.tag)
    };
    req._warehouseData = row;

    // Go to next step
    next();
};
