
#REQ 31
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils import column_discovery, send_json_response, column_discovery2
from pymeos.db.psycopg2 import MobilityDB
from psycopg2 import sql
import json
from pymeos import pymeos_initialize, pymeos_finalize, TGeomPoint
from urllib.parse import urlparse, parse_qs
import math
from datetime import datetime

hostName = "localhost"
serverPort = 8080

host = 'localhost'
port = 25431
db = 'postgres'
user = 'postgres'
password = 'mysecretpassword'

def delete_single_temporal_primitive_geo(self, collectionId, featureId, tGeometryId, connection, cursor):
    columns = column_discovery(collectionId, cursor)
    id = columns[0][0]
    trip = columns[1][0]

    sql_select_trips = f"SELECT asMFJSON({trip}) FROM public.{collectionId} WHERE  {id}={featureId};"
    cursor.execute(sql_select_trips)
    connection.commit()
    rs = cursor.fetchall()
    print(tGeometryId)

    data_dict = json.loads(rs[0][0])
    to_change = data_dict.get("sequences")
    if to_change:
        to_change.pop(int(tGeometryId))
    else:
        to_change = data_dict.get("coordinates")
        to_change.pop(int(tGeometryId))

    print(to_change)

    if (len(to_change) == 1):
        data_dict["coordinates"] = to_change[0]
    else:
        data_dict["sequences"] = to_change

    updated_json = json.dumps(data_dict)
    tgeompoint = TGeomPoint.from_mfjson(updated_json)
    sql_update = f"UPDATE public.{collectionId} SET {trip}= '{tgeompoint}' WHERE {id}={featureId}"
    cursor.execute(sql_update)

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()