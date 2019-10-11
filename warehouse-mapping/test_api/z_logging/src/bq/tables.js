/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
/**
 * Module defining BigQuery data set and table structure.
 *
 * @module BQ
 */
module.exports = {
    PROJECT_ID: 'somctenshi',
    DATA_SETS: {
        TEST: 'test',
        STAGE: 'stage',
        PROD: 'prod'
    },
    TABLES: {
        RAW: 'raw',
        PICK_ROUTE: 'pickroute',
        SINGLE_BATCH: 'singlebatch',
        LOGS: 'logs'
    }
};
