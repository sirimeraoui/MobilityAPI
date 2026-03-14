import json
from datetime import datetime


#validate resources exist by ids::::::::::::::::::::::::::::::::::::::::::::::::::::::
#not used by all files yet check clean:::::::::::
def validate_collection_exists(cursor, collection_id):
    cursor.execute(
        "SELECT id FROM collections WHERE id = %s",
        (collection_id,)
    )
    return cursor.fetchone() is not None

def validate_feature_exists(cursor, feature_id, collection_id):
    cursor.execute(
        "SELECT id FROM moving_features WHERE id = %s AND collection_id = %s",
        (feature_id, collection_id)
    )
    return cursor.fetchone() is not None

def validate_property_exists(cursor, feature_id, property_name):
    cursor.execute("""
        SELECT id FROM temporal_properties
        WHERE feature_id = %s AND property_name = %s
    """, (feature_id, property_name))
    return cursor.fetchone()
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


# clean check, reuse code in other ...
def parse_request_body(self):
    content_length = int(self.headers.get('Content-Length', 0))
    post_data = self.rfile.read(content_length)
    return json.loads(post_data.decode('utf-8'))

#create property -mandatory fields ogc  
def validate_property_data(data):
    errors = []
    if "name" not in data:
        errors.append("Missing required field: name")
    if "type" not in data:
        errors.append("Missing required field: type")
    return errors

