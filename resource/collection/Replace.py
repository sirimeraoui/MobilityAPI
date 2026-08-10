# REQ7: /req/mf-collection/collection-put
# RE10: /req/mf-collection/collection-put-success
import json
from fastapi import HTTPException
from resource.collection.collection_helper import (
    collection_exists,
    update_collection
)

def put_collection(collection_id, data_dict, connection, cursor):
    try:
        # Check if collection exists
        if not collection_exists(cursor, collection_id):
            raise ValueError(f"Collection '{collection_id}' not found")


        # update DB
        update_collection(cursor, collection_id, data_dict)
        connection.commit()

        return True

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    except Exception as e:
        connection.rollback()
        raise e