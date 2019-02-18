
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DBNAME = 'benchmark'

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
IF_MATCH = False
UPSERT_ON_PUT = True

data = {
  'allow_unknown': True,
  'item_title': 'logs',
  'id_field': '_id',
  'item_url': 'regex("[a-zA-Z0-9.-]+")',
  'cache_control': 'max-age=10,must-revalidate',
  'cache_expires': 1,
  'schema': { '_id': { 'type': 'string' } }
}

data2 = {
  'allow_unknown': True,
  'item_title': 'logs',
  'id_field': '_id',
  'item_url': 'regex("[a-zA-Z0-9.-]+")',
  'cache_control': 'max-age=10,must-revalidate',
  'cache_expires': 1,
  'schema': { '_id': { 'type': 'string' } }
}

data3 = {
  'allow_unknown': True,
  'item_title': 'logs',
  'id_field': '_id',
  'item_url': 'regex("[a-zA-Z0-9.-]+")',
  'cache_control': 'max-age=10,must-revalidate',
  'cache_expires': 1,
  'schema': { '_id': { 'type': 'string' } }
}

DOMAIN = {
    'api': data,
    'api2': data2,
    'ratiocompare': data3,
}
