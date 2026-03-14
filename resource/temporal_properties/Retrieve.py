# REQ36: /req/movingfeatures/tproperties-get
# REQ38: /req/movingfeatures/tproperties-get-success

from utils import send_json_response
from resource.temporal_properties.property_helper import build_properties_list_response
import json
import traceback
# GET properties  base/collections/{collectionId}/items/{featureId}/tproperties
def get_tproperties(self, collection_id, feature_id, connection, cursor):
    try:
        #collection exists?
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )
        if cursor.fetchone() is None:
            self.handle_error(404, f"Collection '{collection_id}' not found")
            return
        
        # feature exists?
        cursor.execute(
            "SELECT id FROM moving_features WHERE id = %s AND collection_id = %s",
            (feature_id, collection_id)
        )
        if cursor.fetchone() is None:
            self.handle_error(404, f"Feature '{feature_id}' not found in collection '{collection_id}'")
            return
        
        # Get all properties by feat id
        cursor.execute("""
            SELECT id, property_name, property_type, form, description
            FROM temporal_properties
            WHERE feature_id = %s
            ORDER BY property_name
        """, (feature_id,))
        
        rows = cursor.fetchall()
        
        properties = []
        for row in rows:
            properties.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "form": row[3],
                "description": row[4]
            })
        
        # response
        base_url = f"http://{self.server.server_name}:{self.server.server_port}"
        path = f"/collections/{collection_id}/items/{feature_id}/tproperties"
        
        response = build_properties_list_response(properties, base_url, path)
        send_json_response(self, 200, response)
        
    except Exception as e:
        connection.rollback()
        # print(f"Error in get_tproperties: {e}")
        # traceback.print_exc()
        self.handle_error(500, f"Internal server error: {str(e)}")