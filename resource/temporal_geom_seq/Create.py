# REQ 26: /req/movingfeatures/tgsequence-post
# REQ 28: /req/movingfeatures/tgsequence-post-success
from utils import send_json_response
from pymeos import TGeomPoint
import json

    # POST base/collections/{collectionId}/items/{featureId}/tgsequence
def post_tgsequence(self, connection, cursor):
    try:
        #base/collections/{collectionId}/items/{featureId}/tgsequence
        parsed_path= self.path.split('/')
        collection_id = parsed_path[2]
        feature_id = parsed_path[4]
        
        # LOad request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data_dict = json.loads(post_data.decode('utf-8'))
        
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
            self.handle_error(404, f"Feature '{feature_id}' not found")
            return
        
        # tgseq dict to TGeomPoint pymeos obj ---*
        # str(tgeom) clean check /--/--/ the to pymeos tgeompoint object mayb be not required , to be teste with this endpoint
        # tgeom = json.dumps(data_dict)
        tgeom = TGeomPoint.from_mfjson(json.dumps(data_dict))
        
        # INSERT INTO temporal_geometries 
        cursor.execute("""
            INSERT INTO temporal_geometries 
            (feature_id, geometry_type, trajectory, interpolation)
            VALUES (%s, %s, %s::tgeompoint, %s)
            RETURNING id
        """, (
            feature_id,
            data_dict.get("type", "MovingPoint"),
            str(tgeom),
            data_dict.get("interpolation", "Linear")
        ))
        
        new_id = cursor.fetchone()[0]
        connection.commit()
        
        # codde 201 success + Location
        self.send_response(201)
        self.send_header("Location", f"/collections/{collection_id}/items/{feature_id}/tgsequence/{new_id}")
        send_json_response(self, 201, data_dict)
        
    except Exception as e:
        connection.rollback()
        # print(f"Error in post_tgsequence: {e}")
        self.handle_error(500, f"Internal server error: {str(e)}")