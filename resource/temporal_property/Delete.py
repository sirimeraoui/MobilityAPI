
#REQ 43
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

def delete_temporal_property(self, collectionId, featureId, propertyName, connection, cursor):

    try:

        columns = column_discovery2(collectionId, cursor)

        id_col = columns[0][0]

        # verify column exists
        column_names = [c[0] for c in columns]

        if propertyName not in column_names:
            self.handle_error(404, "Temporal property doesn't exist")
            return

        sql_query = f"""
        UPDATE public.{collectionId}
        SET {propertyName} = NULL
        WHERE {id_col} = %s
        """

        cursor.execute(sql_query, (featureId,))
        connection.commit()

        if cursor.rowcount == 0:
            self.handle_error(404, "Feature not found")
            return

        self.send_response(204)
        self.end_headers()

    except Exception as e:
        connection.rollback()
        self.handle_error(500, str(e))