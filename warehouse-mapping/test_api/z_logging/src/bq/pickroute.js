/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { BigQuery } = require('@google-cloud/bigquery');
const bigQuery = new BigQuery();
const { PROJECT_ID, TABLES } = require('./tables');
const { extract } = require('./utils');
const { timeStamp } = require('./validate');
const { BQ_ERROR } = require('../errors');

async function count (dataSetId, jobId) {
    let job = await bigQuery.createQueryJob({
        query: `SELECT COUNT (*) AS count
                FROM ${PROJECT_ID}.${dataSetId}.${TABLES.PICK_ROUTE}
                WHERE jobId = '${jobId}'`,
        location: 'US'
    });
    let results = await job[0].getQueryResults();
    return results[0][0].count;
}

/**
 * Module implementing pick_run_optimization table related operations.
 *
 * @module PickRoute
 */
module.exports = {
    /**
     * Counts the number of entries in the somctenshi.*.pro Big Query table for a specific jobId.
     *
     * @method count
     * @methodOf PickRoute
     * @param {string} dataSetId ID of the data set to insert pick run into.
     * @param {string} jobId Job ID to count entries for.
     * @returns {Promise<*>} Promise containing the number of rows with the specified job ID.
     * @async
     */
    count,

    /**
     * Inserts a pick run in the somctenshi.*.pro Big Query table.
     *
     * @method insert
     * @memberOf PickRoute
     * @param {string} dataSetId ID of the data set to insert pick run into.
     * @param {string} json String representing the Tenshi JSON response.
     * @async
     */
    async insert (dataSetId, json) {
        return new Promise((resolve, reject) => {
            try {
                let data = {
                    jobId: extract(json, 'jobId'),
                    uuid: extract(json, 'uuid'),
                    warehouseUuid: extract(json, 'warehouseUuid'),
                    pickRunId: extract(json, 'requestData.pickRoundIdentifier'),
                    pickerId: extract(json, 'requestData.userIdentifier'),
                    requestedAt: extract(json, 'webAppData.requestReceivedAtDateTime', timeStamp),
                    respondedAt: extract(json, 'webAppData.responseGeneratedAtDateTime', timeStamp),
                    runType: extract(json, 'runType'),
                    coordinateUnitOfMeasurement: extract(json, 'webAppData.coordinateUnitOfMeasurement'),
                    numberOfLocations: parseInt(extract(json, 'webAppData.numberOfLocations')),
                    pickRun: {
                        totalDistanceMeters: parseFloat(extract(json, 'webAppData.pickRun.totalDistanceMeters')),
                        metersPerPick: parseFloat(extract(json, 'webAppData.pickRun.metersPerPick')),
                        pickNodeCoords: extract(json, 'webAppData.pickRun.pickNodeCoords').map(d => ({
                            x: parseFloat(d.x),
                            y: parseFloat(d.y)
                        })),
                        fullPathCoords: extract(json, 'webAppData.pickRun.fullPathCoords').map(d => ({
                            x: parseFloat(d.x),
                            y: parseFloat(d.y)
                        }))
                    }
                };

                // Send data to BQ
                return bigQuery.dataset(dataSetId)
                    .table(TABLES.PICK_ROUTE)
                    .insert(data)
                    .then(() => {
                        resolve();
                    }).catch(e => {
                        reject(BQ_ERROR(JSON.stringify(e)));
                    });
            } catch (e) {
                reject(e);
            }
        });
    }
};
