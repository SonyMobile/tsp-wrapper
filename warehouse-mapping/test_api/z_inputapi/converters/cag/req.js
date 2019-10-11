/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const _get = require('lodash.get');
const _set = require('lodash.set');

/**
 * Module defining the request mapping fro CAG.
 *
 * @module req
 * @memberOf converters.cag
 */
module.exports = [{
    name: 'apiKey',
    get: x => _get(x, 'MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].ApiKey[0]'),
    set: (x, v) => _set(x, 'requestData.apiKey', v),
    validate: x => typeof x === 'string' && /^\w+$/.test(x)
}, {
    name: 'isClockwise',
    get: x => _get(x, 'MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].IsPickDirectionClockwise[0]'),
    set: (x, v) => _set(x, 'requestData.isClockwise', parseInt(v) !== 0),
    validate: x => typeof x === 'string' && /^(0|1)$/.test(x)
}, {
    name: 'isReroute',
    get: x => _get(x, 'MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].IsReroute[0]'),
    set: (x, v) => _set(x, 'requestData.isReroute', parseInt(v) !== 0),
    validate: x => typeof x === 'string' && /^(0|1)$/.test(x)
}, {
    name: 'mobileUnitIdentifier',
    get: x => _get(x, 'MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].MobileUnitId[0]'),
    set: (x, v) => _set(x, 'requestData.mobileUnitIdentifier', v),
    validate: x => typeof x === 'string' && /^\d+$/.test(x)
}, {
    name: 'pickRoundIdentifier',
    get: x => _get(x, 'MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].PickRoundId[0]'),
    set: (x, v) => _set(x, 'requestData.pickRoundIdentifier', v),
    validate: x => typeof x === 'string' && /^\d+$/.test(x)
}, {
    name: 'pickLocations',
    get: x => {
        const pickLocations = _get(x, 'MaXML_Envelope.PickRoundShow[0].DataArea[0].PickRoundShow[0].PickRound[0].PickLocationList[0].PickLocation');
        return {
            assignmentIdentifier: pickLocations.map(d => _get(d, 'AssignmentId[0]')),
            originalSortingNumber: pickLocations.map(d => _get(d, 'OrigSortOrderNo[0]')),
            rackIdentifier: pickLocations.map(d => _get(d, 'Location[0].Rack[0]')),
            materialHandlingSection: pickLocations.map(d => _get(d, 'Location[0].MHA[0]')),
            rackLocationIdentifier_1: pickLocations.map(d => _get(d, 'Location[0].HorizontalCoordinate[0]')),
            rackLocationIdentifier_2: null
        };
    },
    set: (x, v) => _set(x, 'requestData.pickLocations', v),
    validate: x => Array.isArray(x.assignmentIdentifier) &&
        Array.isArray(x.originalSortingNumber) &&
        Array.isArray(x.rackIdentifier) &&
        Array.isArray(x.materialHandlingSection) &&
        Array.isArray(x.rackLocationIdentifier_1)
}];
