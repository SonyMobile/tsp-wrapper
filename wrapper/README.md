# Service wrapper for pickroute or batching optimization
This is the service(s) that does the actual optimizations. When
deployed, an environment variable, CLIENT_BUCKET, is set to point to
where the data files for the current client/warehouse is
located. These buckets must contains a folder with the data needed for
optimization. This folder must contain the files specified in
client_storage.py and should be the same for all clients.
