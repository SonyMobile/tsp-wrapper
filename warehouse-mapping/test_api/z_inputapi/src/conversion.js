/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { parseString, Builder } = require('xml2js');
const Errors = require('./errors');

module.exports = {
    /**
     * Converts an XML file to the standardized JSON format.
     *
     * @method xml
     * @methodOf conversion
     * @param {string} req Request body as a string.
     * @param {Object} template Object containing the internal request template for the optimizer.
     * @param {Object} mapping Object containing the getter and validator for the fields to extract.
     * @returns {Promise<any>} Promise with the converted JSON object if everything could be extracted, error otherwise.
     * @async
     */
    async fromXml(req, template, mapping) {
        // Convert data
        return new Promise((resolve, reject) => {
            parseString(req, (e, xml) => {
                if (e) {
                    resolve({ error: Errors.INVALID_XML(e.message) });
                }

                // Build request JSON
                try {
                    let json = template;
                    mapping.forEach(d => {
                        let value = d.get(xml);
                        if (typeof value === 'undefined') {
                            reject(Errors.MISSING_KEY(d.name));
                        } else {
                            if (!d.validate(value)) {
                                reject(Errors.INVALID_VALUE(d.name));
                            }
                            d.set(json, value);
                        }
                    });

                    resolve(json);
                } catch (e) {
                    resolve({ error: e });
                }
            });
        });
    },

    async toXml(json, template, mapping) {
        return new Promise(resolve => {
            // Read req-template.json
            parseString(template, (e, xml) => {
                // Fill in data
                mapping.forEach(d => d.set(xml, d.get(json)));

                // Return final response
                resolve(new Builder({
                    headless: true,
                    renderOpts: {
                        pretty: true,
                        indent: '    '
                    }
                }).buildObject(xml));
            });
        });
    }
};
