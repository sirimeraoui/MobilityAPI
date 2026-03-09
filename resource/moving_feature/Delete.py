
#REQ 20
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


def delete_single_moving_feature(self, collectionId, mfeature_id, connection, cursor):
    try:
        sql = f"DELETE FROM public.{collectionId} WHERE id = %s"
        cursor.execute(sql, (mfeature_id,))
        connection.commit()

        if cursor.rowcount == 0:
            self.handle_error(404, f"Feature {mfeature_id} not found")
            return
        self.send_response(204)
        self.end_headers()

    except Exception as e:
        connection.rollback() 
        self.handle_error(500, str(e))