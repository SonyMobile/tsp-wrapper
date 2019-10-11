/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
/**
 * Module implementing test routes for tenshi-api to check if it is up and running.
 *
 * @module test
 */
const router = require('express').Router();
const { X_API_KEY } = require('../src/header');
const Errors = require('../src/errors');


/**
 * Returns status 200 and a success message.
 *
 * @name GET /test
 */
router.get('/', (req, res) => {
    return res.status(200)
        .json({ message: 'tenshi-api is running' })
        .end();
});

/**
 * Returns the x-api-key from the header.
 *
 * @name POST /test
 */
router.post('/', (req, res) => {
    // Check for x-api-key
    if (typeof req.get(X_API_KEY) === 'undefined') {
        return res.status(403)
            .json({ error: Errors.MISSING_API_KEY })
            .end();
    }

    // If API key is present, return a message with the api key.
    return res.status(200)
        .json({ message: `${X_API_KEY} = ${req.get(X_API_KEY)}` })
        .end();
});

module.exports = router;
