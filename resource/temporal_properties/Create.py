
#REQ 39
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



from utils import column_discovery2, handle_error


def post_tproperties(self, collectionId, featureId, connection, cursor):

    try:

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))

        # accept single object or list
        if not isinstance(data, list):
            data = [data]

        columns = column_discovery2(collectionId, cursor)
        existing_columns = [c[0] for c in columns]

        locations = []

        for prop in data:

            name = prop.get("name")
            ttype = prop.get("type")
            form = prop.get("form")

            if not name or not ttype:
                handle_error(self, 400, "Missing required fields")
                return

            if name in existing_columns:
                handle_error(self, 400, f"Property {name} already exists")
                return

            # OGC type TO MobilityDB type MAPPING
            if ttype == "TReal":
                dbtype = "tfloat"
            elif ttype == "TInteger":
                dbtype = "tint"
            elif ttype == "TBoolean":
                dbtype = "tbool"
            elif ttype == "TText":
                dbtype = "ttext"
            else:
                dbtype = "ttext"

            sql = f"""
            ALTER TABLE public.{collectionId}
            ADD COLUMN {name} {dbtype}
            """

            cursor.execute(sql)

            location = f"/collections/{collectionId}/items/{featureId}/tproperties/{name}"
            locations.append(location)

        connection.commit()

        self.send_response(201)
        self.send_header("Locations", ",".join(locations))
        self.end_headers()

    except Exception as e:
        connection.rollback()
        handle_error(self, 500, str(e))