/**
 * Licensed under the LICENSE.
 * Copyright 2019, Sony Mobile Communications Inc.
 */
const knex = require('knex');
const config = require('./src/config.js');

let _db;
function getDb() {
  if(_db) return _db;
  try {
    _db = knex(config.db);
    return _db;
  } catch (err) {
    console.error('Error creating db connection, ', err);
    throw err;
  }
}

module.exports = {
  getClients: async function () {
    try {
      const db = await getDb();
      const rows = await db
            .select()
            .from('warehouses');

        const clients = rows.map(row => ({
          id: row.id,
          name: row.name,
          tag: row.tag,
          apiKey: row.api_key
        }));
      return clients;
    } catch (err) {
      console.error('Error getting clients from db', err);
    }
  },
  insertTask: async function (clientId, type, data) {
    const db = await getDb();
    const ids = await db('tasks')
          .returning('id')
          .insert({
            type,
            warehouse_id: clientId,
            payload: data,
            status: 'waiting'
          });
    return ids[0];
  },
  getTask: async function (id) {
    const db = await getDb();
    const rows = await db
          .select()
          .from('tasks')
          .where({id:id});
    if(rows && rows.length > 0) {
      return rows[0];
    } else {
      throw new Error(`No task with id ${id}`);
    }
  }
};
