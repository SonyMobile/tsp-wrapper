/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
/**
 * Module defining the supported errors.
 *
 * @module Errors
 */
module.exports = {
    /**
     * Source of error is unknown.
     */
    UNKNOWN_ERROR: e => ({
        code: 'E001',
        message: `Unknown error. ${e}`
    }),

    /**
     * API key is missing in the client request.
     */
    MISSING_API_KEY: {
        code: 'E002',
        message: 'Missing API key. Please set the X-Api-Key header or specify it in the request body in accordance with the request content type.'
    },

    /**
     * API key sent with the client request is not a valid key.
     */
    INVALID_API_KEY: {
        code: 'E003',
        message: 'Invalid API key. Please visit https://console.tenshi.ai and check your API key.'
    },

    /**
     * The are multiple warehouses for the specified API key.
     */
    CONFLICTING_API_KEYS: {
        code: 'E004',
        message: 'Conflicting API keys. Contact TenshiAI to resolve the issue.'
    },

    /**
     * Client request does not contain a valid request body for the optimizer.
     */
    EMPTY_REQUEST: {
        code: 'E005',
        message: 'Missing or empty request body.'
    },

    /**
     * Could not connect to the SQL database.
     */
    COULD_NOT_CONNECT: e => ({
        code: 'E006',
        message: `Could not connect to database. ${e}`
    }),

    /**
     * Invalid SQL query.
     */
    INVALID_QUERY: e => ({
        code: 'E007',
        message: `SQL Error. ${e}`
    }),

    /**
     * Something went wrong during optimization.
     */
    OPTIMIZATION_ERROR: e => ({
        code: 'E008',
        message: `Optimization error. ${e}`
    }),

    /**
     * There was an error during the SQL query.
     */
    QUEUE_ERROR: e => ({
        code: 'E009',
        message: `Queuing error. ${e}`
    }),

    /**
     * Task ID is missing from the client request in case of a 202 pattern.
     */
    MISSING_TASK_ID: {
        code: 'E010',
        message: 'Missing task ID. Please specify the task ID in the request.'
    },

    /**
     * There is no task with the specified task ID.
     */
    INVALID_TASK_ID: id => ({
        code: 'E011',
        message: `Invalid task UUID: ${id}. Please check the URL in the response message for the POST request.`
    }),

    /**
     * API key does not belong to the warehouse requesting the resource.
     */
    UNAUTHORIZED_WAREHOUSE: id => ({
        code: 'E012',
        message: `Warehouse ${id} has no permission to access task. Please check if the API key or the task ID is correct.`
    }),

    /**
     * The optimization task failed.
     */
    TASK_FAILED: e => ({
        code: 'E013',
        message: `Task has failed. ${e}`
    }),

    /**
     * Invalid XML. The XML request body could not be parsed.
     */
    INVALID_XML: e => ({
        code: 'E014',
        message: `Invalid XML request. ${e}`
    }),

    /**
     * Required key is missing.
     */
    MISSING_KEY: key => ({
        code: 'E015',
        message: `Missing required field in request: ${key}. Please make sure all required fields are added.`
    }),

    /**
     * Invalid type or format for a value.
     */
    INVALID_VALUE: key => ({
        code: 'E016',
        message: `Value at path is invalid: ${key}. Please contact TenshiAI to resolve the issue.`
    }),

    /**
     * Invalid JSON. The JSON request body could not be parsed.
     */
    INVALID_JSON: e => ({
        code: 'E017',
        message: `Invalid JSON request, please make sure the request body is valid JSON. ${e}`
    }),

    /**
     * Content type is missing in the request header.
     */
    MISSING_CONTENT_TYPE: {
        code: 'E018',
        message: 'Missing Content-Type. Please set the Content-Type header to one of the following: application/json, text/json, application/xml, text/xml.'
    },

    /**
     * Content-type is not supported.
     */
    UNKNOWN_CONTENT_TYPE: e => ({
        code: 'E019',
        message: `Unknown Content-Type: ${e}. Supported types are: application/json, text/json, application/xml, text/xml.`
    })
};
