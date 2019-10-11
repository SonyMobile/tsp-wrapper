/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { v2beta3 } = require('@google-cloud/tasks');
const axios = require('axios');
const config = require('./config');
const { insertTask } = require('./db');
const { X_API_KEY } = require('./header');

const ctClient = new v2beta3.CloudTasksClient();

/**
 * Sends a task to the cloud task queue. Handles both production and development cases. For local development, it simply
 * calls the optimizer endpoint.
 *
 * @method queueTask
 * @param {Object} warehouse Object representing the warehouse data.
 * @param {Object} payload Object containing the request payload for the optimizer.
 * @param {string} targetUrl Endpoint for the optimizer.
 * @param {string} queueName Name of the queue to send task to.
 * @returns {Promise<void>} Empty promise.
 */
async function queueTask(warehouse, payload, targetUrl, queueName) {
    if (process.env.NODE_ENV === 'production') {
        // Convert payload to base 64 string
        const payloadB64 = Buffer.from(JSON.stringify(payload)).toString('base64');

        // Create cloud task request
        const request = {
            parent: ctClient.queuePath(config.project.id, config.project.location, queueName),
            task: {
                httpRequest: {
                    httpMethod: 'POST',
                    url: targetUrl,
                    body: payloadB64,
                    headers: {
                        [X_API_KEY]: warehouse.apiKey
                    }
                }
            }
        };

        // Create cloud task
        const [response] = await ctClient.createTask(request);
        console.log(`Created task ${response.name} as ${JSON.stringify(request)}`);
    } else {
        // In local case, simply send the request but don't wait for response
        axios.post(targetUrl, payload, {
            headers: {
                [X_API_KEY]: warehouse.apiKey
            }
        });
    }
}

module.exports = {
    /**
     * Creates a single batch optimization task.
     *
     * @method createSingleBatchTask
     * @param {Object} warehouse Object representing the warehouse data.
     * @param {Object} data Request body.
     * @returns {Promise<string>} Promise containing the UUID of the created task.
     */
    async createSingleBatchTask (warehouse, data) {
        try {
            // Insert task in database, retrieve UUID
            const taskUuid = await insertTask(
                warehouse.id,
                'singlebatch',
                data
            );

            // Add meta data
            data._meta = {
                taskId: taskUuid,
                warehouse: {
                    uuid: warehouse.uuid,
                    tag: warehouse.tag
                }
            };

            // Send task to queue
            await queueTask(
                warehouse,
                data,
                `${warehouse.paths.optimizerUrl}/singlebatch`,
                config.queues.singleBatchQueueName
            );
            return taskUuid;
        } catch (e) {
            throw e;
        }
    }
};
