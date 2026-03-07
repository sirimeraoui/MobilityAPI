
#REQ 42
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


def post_temporal_property(self, collectionId, featureId, propertyName, connection, cursor):

    try:

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))

        datetimes = data.get("datetimes")
        values = data.get("values")
        interpolation = data.get("interpolation")

        if not datetimes or not values or not interpolation:
            self.handle_error(400, "Missing required fields")
            return

        columns = column_discovery2(collectionId, cursor)
        id_col = columns[0][0]

        # Check ifproperty exists
        column_names = [c[0] for c in columns]

        if propertyName not in column_names:
            self.handle_error(404, "Temporal property does not exist")
            return

        # Retrieve existing temporal value
        sql_select = f"""
        SELECT {propertyName}
        FROM public.{collectionId}
        WHERE {id_col} = %s
        """

        cursor.execute(sql_select, (featureId,))
        result = cursor.fetchone()

        if not result:
            self.handle_error(404, "Feature not found")
            return

        existing = result[0]

        new_sequence = {
            propertyName: {
                "type": "Measure",
                "values": values,
                "interpolation": interpolation
            },
            "datetimes": datetimes
        }

        new_tfloat = TGeomPoint.from_mfjson(json.dumps(new_sequence))

        if existing is None:

            # first temporal value
            sql_update = f"""
            UPDATE public.{collectionId}
            SET {propertyName} = %s
            WHERE {id_col} = %s
            """

            cursor.execute(sql_update, (new_tfloat, featureId))

        else:

            # new temporal sequence
            sql_update = f"""
            UPDATE public.{collectionId}
            SET {propertyName} = {propertyName} || %s
            WHERE {id_col} = %s
            """

            cursor.execute(sql_update, (new_tfloat, featureId))

        connection.commit()

        location = f"/collections/{collectionId}/items/{featureId}/tproperties/{propertyName}"

        self.send_response(201)
        self.send_header("Location", location)
        self.end_headers()

    except Exception as e:

        connection.rollback()
        self.handle_error(500, str(e))