/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const _get = require('lodash.get');
const _set = require('lodash.set');

/**
 * Module defining the response mapping for CAG.
 *
 * @module res
 * @memberOf converters.cag
 */
module.exports = [{
    get: x => _get(x, 'requestData.pickRoundIdentifier'),
    set: (x, v) => _set(x, 'MaXML_Envelope.PickRoundSync[0].DataArea[0].PickRoundSync[0].PickRound[0].PickRoundId[0]', v),
}, {
    get: x => _get(x, 'requestData.mobileUnitIdentifier'),
    set: (x, v) => _set(x, 'MaXML_Envelope.PickRoundSync[0].DataArea[0].PickRoundSync[0].PickRound[0].MobileUnitId[0]', v)
}, {
    get: x => _get(x, 'responseData.originalRouteDistance'),
    set: (x, v) => _set(x, 'MaXML_Envelope.PickRoundSync[0].DataArea[0].PickRoundSync[0].PickRound[0].DistRequest[0]',
        `${parseInt(v)}m`)
}, {
    get: x => _get(x, 'responseData.optimalRouteDistance'),
    set: (x, v) => _set(x, 'MaXML_Envelope.PickRoundSync[0].DataArea[0].PickRoundSync[0].PickRound[0].DistResponse[0]',
        `${parseInt(v)}m`)
}, {
    get: x => _get(x, 'responseData.pickLocations'),
    set: (x, v) => _set(x, 'MaXML_Envelope.PickRoundSync[0].DataArea[0].PickRoundSync[0].PickRound[0].PickLocationList[0]',
        _get(v, 'assignmentIdentifier').map((d, i) => ({
        PickLocation: {
            AssignmentId: d,
            OrigSortOrderNo: v.originalSortingNumber[i],
            Location: {
                MHA: v.materialHandlingSection[i],
                Rack: v.rackIdentifier[i],
                HorizontalCoordinate: v.rackLocationIdentifier_1[i],
                VerticalCoordinate: v.rackLocationIdentifier_2[i] || '001',
                Zone: undefined
            },
            NewSortingNumber: v.optimizedSortingNumber[i]
        }
    })))
}];
