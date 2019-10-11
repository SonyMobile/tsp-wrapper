/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
// Built-in modules
const { readFileSync } = require('fs');

const { isEmpty } = require('lodash');
const router = require('express').Router();
const axios = require('axios');
const Errors = require('../src/errors');
const { X_API_KEY } = require('../src/header');

// Conversion
// TODO Should read response mapping (resMap) according to customer
const { toXml } = require('../src/conversion');
const resMap = require('../converters/cag/res');

// TODO Add XML/JSON conversion

/**
 * Checks for request errors.
 *
 * @method requestErrors
 * @param {Object} data The request data.
 * @returns {(Object|null)} Object describing the error if any, null otherwise.
 */
function requestErrors(data) {
    // Body is missing
    if (typeof data === 'undefined' || isEmpty(data)) {
        return Errors.EMPTY_REQUEST;
    }

    return null;
}

/**
 * Checks for response errors.
 *
 * @method responseErrors
 * @param {Object} response The response object.
 * @returns {(Object|null)} Object describing the error if any, null otherwise.
 */
function responseErrors(response) {
    if (response.status !== 200) {
        return Errors.OPTIMIZATION_ERROR(response.data);
    }

    return null;
}

router.post('/', async (req, res) => {
    try {
        // Get warehouse (set by auth.js)
        const warehouse = req._warehouseData;

        // Read request data and validate
        let data = req.body;
        let reqError = requestErrors(data);
        if (reqError !== null) {
            return res.status(400).json({ error: reqError });
        }

        // Add meta data
        data._meta = {
            warehouse: {
                uuid: warehouse.uuid,
                tag: warehouse.tag
            }
        };

        // Proxy request to optimizer
        if (process.env.NODE_ENV !== 'test') {
            console.log(`Proxying pick route request from ${warehouse.name} to ${warehouse.paths.optimizerUrl}`);
        }
        const response = await axios.post(`${warehouse.paths.optimizerUrl}/pickroute`, data, {
            headers: {
                [X_API_KEY]: warehouse.apiKey
            }
        });

        // Validate response
        let resError = responseErrors(response);
        if (resError !== null) {
            return res.status(500).json({ error: resError });
        }

        // TODO send data to logger, possibly plucking result from response?
        // Return successful response
        switch (req.headers['content-type']) {
            case 'application/json':
            case 'text/json':
                // JSON: simply return optimizer result
                return res.status(200).set({
                    'Content-Type': 'application/json'
                }).json(response.data);
            case 'application/xml':
            case 'text/xml':
                // XML: convert to customer's template XML
                // TODO Should read response template (resTemplate) according to customer
                let resTemplate = readFileSync('./converters/cag/res-template.xml', {encoding: 'utf8'});
                let xmlResponse = await toXml(response.data, resTemplate, resMap);
                return res.status(200).set({
                    'Content-Type': 'application/xml'
                }).send(xmlResponse);
        }

    } catch (e) {
        return res.status(500).json({ error: Errors.UNKNOWN_ERROR(e) });
    }
});

module.exports = router;
