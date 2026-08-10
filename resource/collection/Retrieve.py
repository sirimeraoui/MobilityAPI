# REQ6: /req/mf-collection/collection-get
# REQU 9: /req/mf-collection/collection-get-success
from resource.collection.collection_helper import (
    fetch_collection_by_id,
    build_collection_response
)
import json
# clean : use this in collections/retrieve.py?
def get_collection_id(connection, cursor, collection_id, base_url: str):
    try:
        collection = fetch_collection_by_id(cursor, collection_id)

        if not collection:
            raise ValueError(f"Collection '{collection_id}' not found")

        response = build_collection_response(collection, base_url)

        return response

    except Exception:
        raise