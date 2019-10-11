/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
/**
 * Module implementing various validation methods for tenshi-worker.
 *
 * @module validate
 */
module.exports = {
    /**
     * Validates a time stamp. Time stamps must be in ISO 8601 format optionally with milliseconds and nanoseconds,
     * that is:
     *
     * YYYY-mm-dd HH:MM:SS[.SSS[SSS]]
     *
     * @method timeStamp
     * @memberOf validate
     * @param {string} x Time stamp as a string.
     * @returns {boolean} True if time stamp is in the right format, false otherwise.
     */
    timeStamp: {
        func: x => /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(.\d{3,6})?$/.test(x),
        desc: 'Time stamp must be in ISO 8601 format with optional milli- and nanoseconds: YYYY-mm-dd HH:MM:SS[.SSS[SSS]]'
    }
};
