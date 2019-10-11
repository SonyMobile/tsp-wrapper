/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
/**
 * Module defining tenshi-worker errors. Error codes for tenshi-worker start at 201.
 *
 * @module errors
 */
module.exports = {
    /**
     * The request source is unknown. Known (and handled) sources are: PubSub, Postman, curl.
     */
    UNKNOWN_SOURCE: {
        code: 'E201',
        message: 'Unknown source, could not read req.body.message.data.'
    },

    /**
     * The request body is not a valid JSON.
     */
    INVALID_JSON: e => ({
        code: 'E202',
        message: `Could not parse JSON. ${e}.`
    }),

    /**
     * The job ID is missing for the BQ entry.
     */
    MISSING_JOB_ID: {
        code: 'E203',
        message: 'Missing jobId.'
    },

    /**
     * A required key is missing in the request data.
     */
    MISSING_KEY: key => ({
        code: 'E204',
        message: `Missing key in JSON: ${key}.`
    }),

    /**
     * A request value has an invalid format. In other words, it did not pass the validation test.
     */
    INVALID_FORMAT: (key, desc) => ({
        code: 'E205',
        message: `Invalid data format for '${key}'. ${desc}.`
    }),

    /**
     * There was something wrong with the BQ query.
     */
    BQ_ERROR: e => ({
        code: 'E206',
        message: `BQ error. ${e}.`
    })
};
