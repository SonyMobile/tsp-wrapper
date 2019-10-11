/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const get = require('lodash.get');
const { MISSING_KEY, INVALID_FORMAT } = require('../errors');

/**
 * Module implementing some utility methods for BQ.
 *
 * @module utils
 */
module.exports = {
    /**
     * Tries to extract a value from an object given a path. If not found, throws an error.
     *
     * @method extract
     * @methodOf utils
     * @param {Object} obj Object to retrieve value from.
     * @param {string} key Path to the value to extract.
     * @param {Function?} validator Optional method to validate the value under the key.
     * @returns {(string|number|Array)} The extracted value if it exists.
     * @returns {Object} validator Optional validator.
     * @throws Error with the error message if a value is not in path.
     */
    extract (obj, key, validator) {
        // Try to extract value
        let value = get(obj, key);
        if (typeof value === 'undefined') {
            throw MISSING_KEY(key);
        } else {
            // Validate if validator is specified
            if (validator && !validator.func(value)) {
                throw INVALID_FORMAT(key, validator.desc);
            }
            return value;
        }
    }
};
