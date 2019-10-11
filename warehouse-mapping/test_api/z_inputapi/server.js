/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const getServer = require('./src/server-factory');

// Start Google Cloud debug agent
if(process.env.NODE_ENV === 'production') {
    require('@google-cloud/debug-agent').start();
}

const PORT = process.env.PORT || 3000;

// Build server
(async function() {
    const a = (await getServer());
    a.listen(PORT, () => console.log(`Server listening on port ${PORT}!`));
})();
