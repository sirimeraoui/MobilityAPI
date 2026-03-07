
#REQ 38
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

def get_tproperties(self,connection, cursor):
    collection_id = self.path.split('/')[2]
    feature_id = self.path.split('/')[4]

    if self.path.endswith("/tproperties"):
        self.do_get_set_temporal_data(collection_id, feature_id)
    else:
        tpropertyname = self.path.split('/')[6]
        self.do_get_temporal_property(
            collection_id, feature_id, tpropertyname)


def get_set_temporal_data(self, collectionId, featureId,connection, cursor):
    columns = column_discovery2(collectionId, cursor)
    id = columns[0][0]
    trip = columns[1][0]

    string = f"SELECT "

    for i in range(2, len(columns)):
        string += columns[i][0] + ","

    string = string.rstrip(",")
    string += f" FROM public.{collectionId} WHERE {id} = {featureId}"
    cursor.execute(string)
    rs = cursor.fetchall()

    tab = []
    for element in rs[0]:
        mf_json = element.as_mfjson()

        tab.append(json.loads(mf_json))
    print(tab)
    json_data = {
        "temporalProperties": tab,
        "timeStamp": "2021-09-01T12:00:00Z",
        "numberMatched": 10,
        "numberReturned": 2
    }

    send_json_response(self, 200, json.dumps(json_data))

    return


# def get_temporal_properties(self, collectionId, featureId, connection, cursor):

#     columns = column_discovery2(collectionId, cursor)

#     id_col = columns[0][0]

 
#     temporal_cols = columns[2:]

#     temporal_properties = []

#     for col in temporal_cols:

#         name = col[0]

#         temporal_properties.append({
#             "name": name,
#             "type": "TReal",   +
#             "form": "unknown"
#         })

#     base_url = f"http://{hostName}:{serverPort}"

#     response = {
#         "temporalProperties": temporal_properties,
#         "links": [
#             {
#                 "href": f"{base_url}/collections/{collectionId}/items/{featureId}/tproperties",
#                 "rel": "self",
#                 "type": "application/json"
#             }
#         ],
#         "timeStamp": datetime.utcnow().isoformat() + "Z",
#         "numberMatched": len(temporal_properties),
#         "numberReturned": len(temporal_properties)
#     }

#     send_json_response(self, 200, json.dumps(response))    

