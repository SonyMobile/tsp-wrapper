/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */

/**
 * Module implementing low-level database operations.
 *
 * @module db
 */
const uuidv1 = require('uuid/v1');
const knex = require('knex');
const config = require('./config');
const Errors = require('./errors');

/**
 * Gets or creates the SQL database handler.
 *
 * @method getDB
 * @async
 */
const getDB = (function () {
    let db;
    return async function () {
        if (typeof db === 'undefined') {
            try {
                db = knex(config.db);
            } catch (e) {
                throw { error: Errors.COULD_NOT_CONNECT(e) };
            }
        }
        return Promise.resolve(db);
    };
})();


module.exports = {
    /**
     * Returns a warehouse by its API key.
     *
     * @method getWarehousesByApiKey
     * @param {string} apiKey API key to select warehouses by.
     * @returns {Promise<{error: *}>} Promise containing the warehouses.
     * @async
     */
    // TODO Include check for multiple/zero warehouses
    async getWarehousesByApiKey(apiKey) {
        try {
            // Select warehouses that match the API key
            const db = await getDB();
            return await db.select('id', 'uuid', 'name', 'tag')
                .from('warehouses')
                .where({ api_key: apiKey });
        } catch (e) {
            if (e.code !== 'E004') {
                return Promise.resolve({ error: Errors.INVALID_QUERY(e) });
            } else {
                throw e;
            }
        }
    },

    /**
     * Inserts a task to the tasks table and returns the task ID.
     *
     * @method insertTask
     * @param {string} id ID of the warehouse to create task for.
     * @param {string} type Task type to create.
     * @param {Object} data Input data for the task.
     * @returns {Promise<string>} Promise containing the task UUID.
     */
    async insertTask (id, type, data) {
        // Generate v1 UUID, insert task
        const db = await getDB();
        let taskUuid = uuidv1();
        await db('tasks')
            .insert({
                uuid: taskUuid,
                type,
                warehouse_id: id,
                payload: JSON.stringify(data),
                // TODO Move this to a constant
                status: 'waiting'
            });

        // Return UUID
        return taskUuid;
    },

    /**
     * Retrieves a task by its UUID.
     *
     * @getTask
     * @param {string} uuid UUID of the task to retrieve.
     * @returns {Promise<*>} Promise containing the task status, result and warehouse ID.
     */
    async getTask (uuid) {
        const db = await getDB();
        const rows = await db.select('status', 'result', 'warehouse_id')
            .from('tasks')
            .where({ uuid });

        // Check if UUID corresponds to any task
        if (!rows || rows.length === 0) {
            return undefined;
        }

        // Return results
        return rows[0];
    }
};
