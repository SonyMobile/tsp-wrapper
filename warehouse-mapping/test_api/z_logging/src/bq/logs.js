/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { PROJECT_ID, TABLES } = require('./tables');
const { BigQuery } = require('@google-cloud/bigquery');
const bigquery = new BigQuery();

/**
 * Module implementing logs table related operations.
 *
 * @module Logs
 */
module.exports = {
    /**
     * Inserts a log entry to the logs table.
     *
     * @method insert
     * @methodOf Logs
     * @param {string} dataSetId ID of the data set to insert pick run into.
     * @param {string} table Name of table to insert log entry for.
     * @param {?string} uuid UUID of the JSON object the log is added for.
     * @param {string=} error Optional error message.
     */
    async insert (dataSetId, table, uuid, error) {
        if (error) {
            console.log(`Failed to insert json entry: ${error}`);
        }
        await bigquery.dataset(dataSetId)
            .table(TABLES.LOGS)
            .insert({
                at: Date.now(),
                table,
                uuid,
                success: typeof error === 'undefined',
                error: error || null
            })
            .catch(e => {
                console.error(`Could not add log: ${e.message}`);
            });
    },

    /**
     * Selects the latest log entries from the logs table.
     *
     * @method select
     * @methodOf Logs
     * @param {string} dataSetId ID of the data set to insert pick run into.
     * @param {(string|number)} limit Number of log entries to return.
     * @param {(string|number)} offset Number of log entries to skip.
     * @returns {Object[]} JSON array of the latest log entries sorted by time in descending order.
     */
    async select (dataSetId, limit = 100, offset = 0) {
        let job = await bigquery.createQueryJob({
            query: `SELECT *
                FROM ${PROJECT_ID}.${dataSetId}.${TABLES.LOGS}
                ORDER BY \`at\` DESC
                LIMIT ${limit} OFFSET ${offset}`,
            location: 'US'
        });

        // Return results
        return await job[0].getQueryResults();
    }
};
