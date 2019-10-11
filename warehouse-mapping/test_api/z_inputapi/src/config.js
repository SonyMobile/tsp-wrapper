/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */

/**
 * Reads an API URL from an environmental variable.
 *
 * @method urlFromEnvVar
 * @param {string} prefix Prefix of the environmental variable.
 * @param {string} clientTag Tag describing the client.
 * @returns {string} The parsed URL.
 */
function urlFromEnvVar(prefix, clientTag) {
    const optimizerUrlEnvVar = `${prefix}${clientTag}`;
    let url = process.env[optimizerUrlEnvVar];
    if (!url) {
        console.warn(`Environment variable ${optimizerUrlEnvVar} not set!`);
        url = 'http://localhost:8080';
    }
    if (process.env.NODE_ENV !== 'test') {
        console.log(`Using url ${url} for client ${clientTag}`);
    }
    return url;
}

/**
 * Returns the password for the SQL database.
 *
 * @method getDBPassword
 * @returns {Promise<string>} Promise containing the SQL database password.
 */
async function getDBPassword() {
    return Promise.resolve(process.env.TENSHI_DB_PASSWORD);
}

/**
 * Static content of the SQL database configuration.
 *
 * @var {Object} config
 */
const config = {
    project: {
        id: process.env.GOOGLE_CLOUD_PROJECT,
        location: 'europe-west1',
    },

    db: process.env.NODE_ENV === 'production' ? {
        client: 'mysql',
        connection: {
            // For production, use socket path
            socketPath: `/cloudsql/${process.env.TENSHI_DB_CONNECTION_NAME}`,
            database: process.env.TENSHI_DB_NAME,
            user: process.env.TENSHI_DB_USER_NAME
        }
    } : {
        client: 'mysql',
        connection: {
            // For development and testing, use localhost
            host: 'localhost',
            database: process.env.TENSHI_DB_NAME,
            user: process.env.TENSHI_DB_USER_NAME
        }
    },

    queues: {
        singleBatchQueueName: process.env.TENSHI_SINGLEBATCH_QUEUENAME || 'singlebatch-queue',
    },

    endpoints: {
        legacyOptimizerUrl_DADC: process.env.TENSHI_LEGACY_OPTIMIZER_URL_DADC || 'http://localhost:8080/optimize',
        legacyOptimizerUrl_CAG: process.env.TENSHI_LEGACY_OPTIMIZER_URL_CAG || 'http://localhost:8080/optimize',
        getOptimizerUrl: warehouseTag => urlFromEnvVar('TENSHI_OPTIMIZER_URL_', warehouseTag.toUpperCase())
    },

    /**
     * Initializer: sets asynchronously obtained configurations.
     *
     * @method initialize
     * @methodOf config
     */
    initialize: (function () {
        // Set initialized to false
        let isInitialized = false;

        // Return initializer function
        return async function () {
            // If already initialized, throw error: should not initialize more than once.
            if (isInitialized) {
                //throw new Error('Config already initialized');
            }
            isInitialized = true; //A bit early, but since async...

            // Config that must be done async goes here
            config.db.connection.password = await getDBPassword();

            if (process.env.NODE_ENV !== 'test') {
                console.log(`Config initialized: ${JSON.stringify(config)}`);
            }
        };
    })()
};

module.exports = config;
