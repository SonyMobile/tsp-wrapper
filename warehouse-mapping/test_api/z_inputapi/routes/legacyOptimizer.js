/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const axios = require('axios');
const parseString = require('xml2js').parseString;
const express = require('express');
const config = require('../src/config.js');

const router = express.Router();

const CLIENTS = [
    {
        tag: 'CAG',
        name: 'Consafe/Gardemoen',
        apiKey: 'aADX3UzP',
    },
    {
        tag: 'DADC',
        name: 'DADC',
        apiKey: 'dDDZ6TyP',
    },
    {
        tag: 'DADC',
        name: 'Admin DADC',
        apiKey: 'adminDADC',
    },
    {
        tag: 'CAG',
        name: 'Admin CAG',
        apiKey: 'adminCAG',
    },
    {
        tag: 'DADC',
        name: 'Service Demo',
        apiKey: 'service_demo',
    },
];

// This maps api key (key) to url (value).
const clientRoutes = {};
CLIENTS.forEach(client => {
  clientRoutes[client.apiKey] =
    client.tag === "CAG" ?
        config.endpoints.legacyOptimizerUrl_CAG :
        config.endpoints.legacyOptimizerUrl_DADC;
});

async function getRawBody(req) {
    return new Promise((resolve, reject) => {
        req.setEncoding('utf8');
        let rawBody = '';
        req.on('data', function(chunk) {
            rawBody += chunk;
        });
        req.on('end', function() {
            resolve(rawBody);
        });
    });
}

async function getApiKey(req, contentType, rawBody) {
    return new Promise((resolve, reject) => {
        let apiKey;
        if (contentType === 'text/xml') {
            // Special case for Consafe / Ahlsell that uses XML and have the API key
            // in the XML instead of header.
            try {
                parseString(rawBody, function (error, result) {
                    if (error) {
                        console.log(error);
                        res.staus(400 /*bad request*/).send();
                        return;
                    }
                    if (result &&
                        result.MaXML_Envelope &&
                        result.MaXML_Envelope.PickRoundShow[0] &&
                        result.MaXML_Envelope.PickRoundShow[0].DataArea[0] &&
                        result.MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0] &&
                        result.MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0] &&
                        result.MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].ApiKey) {
                            apiKey = result.MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].ApiKey[0];
                    }
                });
            } catch (err) {
                console.error('Error parsing xml', err);
            }
        } else if (contentType === 'application/json') {
            apiKey = req.get('x-api-key');
        }

        resolve(apiKey);
    });
}

router.post('/', async (req, res) => {
    const contentType = req.get('Content-Type');

    if (contentType !== 'application/json' && contentType !== 'text/xml') {
        res.status(400 /*bad request*/).send('Only JSON or XML is supported.');
        return;
    }

    const rawBody = await getRawBody(req);

    const apiKey = await getApiKey(req, contentType, rawBody);
    if (!apiKey || (apiKey && !clientRoutes[apiKey])) {
        res.status(401 /*unauthorized*/).send('Unauthorized');
        return;
    }

    const url = `${clientRoutes[apiKey]}`;
    console.log('Posting to ', url, rawBody);

    try {
        const response = await axios({
            method: 'POST',
            url,
            data: rawBody,
            headers: {
                'Content-Type': contentType,
                'x-api-key': apiKey
            }
        });
        if (response.status !== 200) {
            console.error('Failed to route. Status: ' + response.statusCode);
            res.status(response.statusCode).send();
            return;
        }
        res.send(response.data);

    } catch (err) {
        res.status(500).send(err);
    }
});

module.exports = router;
