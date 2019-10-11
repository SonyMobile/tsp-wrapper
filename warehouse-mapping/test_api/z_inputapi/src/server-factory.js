/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
// Other imports
const express = require('express');
const bodyParser = require('body-parser');
const authorize = require('../middleware/auth.js');

// Configurations
const config = require('./config.js');

// Routers
const testRouter = require('../routes/test');
const legacyOptimizer = require('../routes/legacyOptimizer.js');
const pickRouteOptimizer = require('../routes/pickRouteOptimizer.js');
const singleBatchOptimizer = require('../routes/singleBatchOptimizer.js');

// Errors
const Errors = require('./errors');

// Conversion
const { fromXml } = require('../src/conversion');
const template = require('../converters/_tenshi/req-template');
// TODO Should read request mapping (reqMap) according to customer
const reqMap = require('../converters/cag/req');

/**
 * Module implementing a server factory:
 * - Initializes database configurations.
 * - Adds authorization and body parsing middlewares.
 * - Assigns endpoints.
 *
 * The main reason for encapsulating this step in a separate module is to be able to run it from the test suites. It is
 * mainly used by server.js and the scripts in test/.
 *
 * @method getServer
 * @returns {Promise<*|Function>} Promise containing the initialized server.
 */
module.exports = async function () {
    // Initialize configuration: this is the only reason for making this factory async, as we fetch database
    // configurations in an async manner.
    await config.initialize();

    // Create app
    const app = express();

    // Parse raw body for JSON and XML
    app.use('/v1/*', bodyParser.text({ type: 'application/json' }));
    app.use('/v1/*', bodyParser.text({ type: 'text/json' }));
    app.use('/v1/*', bodyParser.text({ type: 'application/xml' }));
    app.use('/v1/*', bodyParser.text({ type: 'text/xml' }));

    // Convert body based on content type
    app.use('/v1/*', async (req, res, next) => {
        // Only for POST requests
        if (req.method !== 'POST') {
            return next();
        }

        // Check if content type is missing
        const contentType = req.headers['content-type'];
        if (!contentType) {
            return res.status(400).json({ error: Errors.MISSING_CONTENT_TYPE });
        }

        // Check if body is empty
        if (req.body === '') {
            return res.status(400).json({ error: Errors.EMPTY_REQUEST });
        }

        // Parse body
        switch (contentType) {
            case 'application/json':
            case 'text/json':
                try {
                    req.body = JSON.parse(req.body);
                    next();
                } catch (e) {
                    return res.status(400).json({ error: Errors.INVALID_JSON(e) });
                }
                break;
            case 'application/xml':
            case 'text/xml':
                fromXml(req.body, template, reqMap)
                    .then(d => {
                        req.body = d;
                        next();
                    })
                    .catch(e => {
                        res.status(400).json({ error: e });
                    });
                break;
            default:
                return res.status(400).json({ error: Errors.UNKNOWN_CONTENT_TYPE(contentType) });
        }
    });

    // Once we parsed the body, run the authorization (because some customers cannot set X-Api-Key header...)
    app.use('/v1/*', authorize);

    // Set up routers
    app.use('/test', testRouter);
    app.use('/v1/optimize/pickroute', pickRouteOptimizer);
    app.use('/v1/optimize/singlebatch', singleBatchOptimizer);
    app.use('/optimize', legacyOptimizer);

    // Return app
    return app;
};
