/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
'use strict';
const logsRouter = require('./routes/logs');
const pickRouteRouter = require('./routes/pickroute');
const singleBatchRouter = require('./routes/singlebatch');
const storeInBucket = require('./legacy/store-in-bucket');
const storeInBigQuery = require('./legacy/store-in-bigquery');

// Setup express.
let express = require('express');
let bodyParser = require('body-parser');
let app = express();
app.use(bodyParser.urlencoded({limit: '50mb', extended: true}));
app.use(bodyParser.json({limit: '50mb', extended: true}));

// General route
app.get('/', (req, res) => {
    res.status(200).send('tenshi-worker is running');
});

// Supported endpoints: each endpoint is responsible for a single table.
app.use('/', logsRouter);
app.use('/', pickRouteRouter);
app.use('/', singleBatchRouter);

// TODO Remove legacy endpoints
// Legacy routes
// This route will store the log in a Google Cloud bucket.
app.post('/worker-bucket-log', (req, res) => {
    storeInBucket(req, res);
});
// This route will store the log in Google Cloud BigQuery.
app.post('/worker-bigquery-log', (req, res) => {
    storeInBigQuery(req, res);
});

// Start server
const port = process.env.PORT || process.env.TENSHI_WORKER_PORT;
app.listen(port, () => {
    console.log(`App listening on port ${port}`);
});
