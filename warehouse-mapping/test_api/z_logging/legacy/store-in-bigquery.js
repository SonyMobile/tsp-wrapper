/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const { BigQuery } = require('@google-cloud/bigquery');
const bigquery = new BigQuery();

module.exports = async function storeInBigQuery(req, res) {
    console.log('Store in BigQuery');

    // Data comes in as encoded string so we need to decode it.
    const data = Buffer.from(req.body.message.data, 'base64').toString('utf-8');
    const jsonData = JSON.parse(data).WebAppData;

    const datasetId = 'tenshi';
    const tableId = 'webappdata';

    const bigQueryData = {
        id: jsonData.id,
        warehouseId: jsonData.warehouseId,
        coordinate_unit_of_measurement: jsonData.coordinate_unit_of_measurement,
        ResponseTimeTaken: jsonData.ResponseTimeTaken,
        bef_optimization: {
            RackLocationID_1: jsonData.bef_optimization.RackLocationID_1,
            MaterialHandlingSection: jsonData.bef_optimization.MaterialHandlingSection,
            timestamps: jsonData.bef_optimization.timestamps,
            totalDistanceMeters: jsonData.bef_optimization.totalDistanceMeters,
            avgVelocityMetersPerSecond: jsonData.bef_optimization.avgVelocityMetersPerSecond,
            user: jsonData.bef_optimization.user,
            RackID: jsonData.bef_optimization.RackID,
            metersperpick: jsonData.bef_optimization.metersperpick,
            pickNodeCoords: jsonData.bef_optimization.pickNodeCoords,
            RackLocationID_2: jsonData.bef_optimization.RackLocationID_2 === null ? [] : jsonData.bef_optimization.RackLocationID_2,
            fullPathCoords: jsonData.bef_optimization.fullPathCoords
        },
        ResponseGeneratedAtDateTime: jsonData.ResponseGeneratedAtDateTime,
        RequestRecievedAtDateTime: jsonData.RequestRecievedAtDateTime,
        PickRunID: jsonData.PickRunID,
        Number_of_Locations: jsonData.Number_of_Locations,
        aft_optimization: {
            RackLocationID_1: jsonData.aft_optimization.RackLocationID_1 === null ? [] : jsonData.aft_optimization.RackLocationID_1,
            MaterialHandlingSection: jsonData.aft_optimization.MaterialHandlingSection === null ? [] : jsonData.aft_optimization.MaterialHandlingSection,
            timestamps: jsonData.aft_optimization.timestamps === null ? [] : jsonData.aft_optimization.timestamps,
            totalDistanceMeters: jsonData.aft_optimization.totalDistanceMeters,
            DistanceSavedMeters: jsonData.aft_optimization.DistanceSavedMeters,
            user: jsonData.aft_optimization.user,
            RackLocationID_2: jsonData.aft_optimization.RackLocationID_2 === null ? [] : jsonData.aft_optimization.RackLocationID_2,
            metersperpick: jsonData.aft_optimization.metersperpick,
            pickNodeCoords: jsonData.aft_optimization.pickNodeCoords === null ? [] : jsonData.aft_optimization.pickNodeCoords,
            avgVelocityMetersPerSecond: jsonData.aft_optimization.avgVelocityMetersPerSecond,
            RackID: jsonData.aft_optimization.RackID === null ? [] : jsonData.aft_optimization.RackID,
            fullPathCoords: jsonData.aft_optimization.fullPathCoords === null ? [] : jsonData.aft_optimization.fullPathCoords
        }
    };

    try {
        await bigquery
            .dataset(datasetId)
            .table(tableId)
            .insert(bigQueryData);

        console.log(`Store in bigquery success.`);
        res.status(200).send('OK').end();
    } catch (error) {
        console.error(`Error storing in big query. Error=${JSON.stringify(error)}`);
        res.status(500).send().end();
    }
};
