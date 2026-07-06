# REQ1: /req/mf-collection/collections-get
# REQ 3: /req/mf-collection/collections-get-success
from http.server import BaseHTTPRequestHandler, HTTPServer
from utils import send_json_response
import json
from resource.collection.collection_helper import (
    fetch_all_collections,
    build_collection_response,
    build_collections_list_response
)

def get_collections(connection, cursor, base_url: str):
    try:
        collections_data = fetch_all_collections(cursor)

        collections_list = []

        for collection in collections_data:
            collections_list.append(
                build_collection_response(collection, base_url)
            )

        response = build_collections_list_response(collections_list, base_url)

        return response

    except Exception as e:
        print(f"Error in get_collections: {e}")
        raise