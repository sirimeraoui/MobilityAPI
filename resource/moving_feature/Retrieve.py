
#REQ 19
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


def get_movement_single_moving_feature(self, collectionId, mFeatureId, connection, cursor):
    try:
        sql = f"""
        SELECT
            id,
            xmin(stbox(temporalgeometry::tgeompoint)) AS minx,
            ymin(stbox(temporalgeometry::tgeompoint)) AS miny,
            xmax(stbox(temporalgeometry::tgeompoint)) AS maxx,
            ymax(stbox(temporalgeometry::tgeompoint)) AS maxy,
            tmin(stbox(temporalgeometry::tgeompoint)) AS start_time,
            tmax(stbox(temporalgeometry::tgeompoint)) AS end_time
        FROM public.{collectionId}
        WHERE id = %s;
        """

        cursor.execute(sql, (mFeatureId,))
        row = cursor.fetchone()

        if row is None:
            self.handle_error(404, "Moving feature not found")
            return

        bbox = [row[1], row[2], row[3], row[4]]
        time_extent = [row[5].isoformat(), row[6].isoformat()]

        feature = {
            "type": "Feature",
            "id": str(row[0]),
            "geometry": None,  
            "properties": {},
            "bbox": bbox,
            "time": time_extent
        }

        send_json_response(self, 200, json.dumps(feature))

    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass

        import traceback
        traceback.print_exc()

        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "Internal Server Error",
            "message": str(e)
        }).encode("utf-8"))