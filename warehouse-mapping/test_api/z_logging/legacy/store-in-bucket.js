/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
module.exports = function storeInBucket(req, res)
{
    console.log('Store in bucket');
    const uuidv1 = require('uuid/v1');
    const { Storage } = require('@google-cloud/storage');

    let storage = new Storage({
        projectId: 'somctenshi'
    }).bucket('somctenshi.appspot.com');

    console.log(`Worker bucket log.`);

    // Data comes in as encoded string so we need to decode it.
    const data = Buffer.from(req.body.message.data, 'base64').toString('utf-8');

    let filename = Date.now() + '_' + uuidv1() + '.json';

    let gcsStream = storage.file('logs/' + filename).createWriteStream();
    gcsStream.write(data);
    gcsStream.end();

    gcsStream.on('error', (err) => {
        console.error(`Error storage file write. Error=${JSON.stringify(err)}`);

        // Something went wrong. Respond with 500 and Pub/Sub will retry.
        res.status(500).send().end();
    });

    gcsStream.on('finish', (err) => {
        if (err) {
            // TODO Handle error
        }
        console.log('File written successfully to bucket.');
        res.status(200).send('OK').end();
    });
};
