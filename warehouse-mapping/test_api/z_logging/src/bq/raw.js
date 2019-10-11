/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { TABLES } = require('./tables');
const { BigQuery } = require('@google-cloud/bigquery');
const bigquery = new BigQuery();

/**
 * Module implementing raw table related operations.
 *
 * @module Raw
 */
module.exports = {
    /**
     * Inserts a raw JSON to the raw table.
     *
     * @method insert
     * @methodOf Raw
     * @param {string} dataSetId ID of the data set to insert pick run into.
     * @param {string} jobId UUID of the job for the JSON to insert.
     * @param {string} json String representing the data to insert.
     * @returns {Promise<void>}
     */
    async insert(dataSetId, jobId, json) {
        return bigquery.dataset(dataSetId)
            .table(TABLES.RAW)
            .insert({
                timestamp: Date.now(),
                jobId,
                json
            });
    }
};
