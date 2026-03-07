
#REQ 48
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils import column_discovery, send_json_response, column_discovery2
from pymeos.db.psycopg2 import MobilityDB
from psycopg2 import sql
import json
from pymeos import pymeos_initialize, pymeos_finalize, TGeomPoint
from urllib.parse import urlparse, parse_qs
import math
from datetime import datetime
from resource.temporal_property.Retrieve import get_temporal_property
hostName = "localhost"
serverPort = 8080

host = 'localhost'
port = 25431
db = 'postgres'
user = 'postgres'
password = 'mysecretpassword'



def delete_temporal_primitive_value(self, collectionId, featureId, propertyName, tValueId, connection, cursor):
    #get temp property
    cursor.execute(f"SELECT {propertyName} FROM public.{collectionId} WHERE id={featureId}")
    result = cursor.fetchone()
    if not result:
        self.handle_error(404, "Feature or property not found")
        return

    # load MF-JSON
    prop_data = json.loads(result[0])

    #del y value
    values = prop_data.get("values", [])
    for i, val in enumerate(values):
        if val.get("id") == int(tValueId):
            values.pop(i)
            break
    else:
        self.handle_error(404, "TemporalPrimitiveValue not found")
        return


    updated_json = json.dumps(prop_data)
    cursor.execute(f"UPDATE public.{collectionId} SET {propertyName} = '{updated_json}' WHERE id={featureId}")
    connection.commit()

    self.send_response(200)
    self.end_headers()