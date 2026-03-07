
#REQ 41
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


def get_temporal_property(self, collectionId, featureId, propertyName, connection, cursor):
    columns = column_discovery2(collectionId, cursor)
    id = columns[0][0]
    trip = columns[1][0]
    sqlString = f"SELECT asMFJSON({trip}) FROM public.{collectionId} WHERE {id} = {featureId} "
    cursor.execute(sqlString)
    rs = cursor.fetchall()
    print(rs[0][0])
    data = json.loads(rs[0][0])
    temporal_property = data.get(f"{propertyName}")