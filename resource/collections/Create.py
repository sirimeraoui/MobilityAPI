# REQ 2: /req/mf-collection/collections-post
# REQ 4: /req/mf-collection/collections-post-success

from http.server import BaseHTTPRequestHandler, HTTPServer
from utils import send_json_response
from resource.collection.collection_helper import (
    validate_collection_data,
    collection_exists,
    insert_collection,
    build_collection_response
)
import json

import json
from resource.collection.collection_helper import (
    validate_collection_data,
    collection_exists,
    insert_collection
)

def post_collections(connection, cursor, data_dict, base_url):
    try:
        # Attribute data validation
        errors, validated_data = validate_collection_data(
            data_dict,
            is_update=False
        )

        if errors:
            raise ValueError("; ".join(errors))

        collection_id = validated_data.pop("id")

        # create tables if not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                update_frequency INTEGER,
                item_type TEXT DEFAULT 'movingfeature',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moving_features (
                id TEXT PRIMARY KEY,
                collection_id TEXT REFERENCES collections(id) ON DELETE CASCADE,
                type TEXT DEFAULT 'Feature',
                properties JSONB,
                bbox STBOX,
                time TSTZSPAN,
                crs JSONB DEFAULT '{"type":"Name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}'::jsonb,
                trs JSONB DEFAULT '{"type":"Name","properties":{"name":"urn:ogc:data:time:iso8601"}}'::jsonb,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_geometries (
                id SERIAL PRIMARY KEY,
                feature_id TEXT REFERENCES moving_features(id) ON DELETE CASCADE,
                collection_id TEXT REFERENCES collections(id) ON DELETE CASCADE,
                geometry_type TEXT,
                geometry geometry,
                trajectory tgeompoint,
                interpolation TEXT,
                base JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        connection.commit()

        # check existence
        if collection_exists(cursor, collection_id):
            raise ValueError(f'Collection "{validated_data.get("title")}" already exists.')

        insert_collection(cursor, collection_id, validated_data)
        connection.commit()

        # response payload (no HTTP here)
        collection_data = {
            "id": collection_id,
            "title": validated_data.get("title"),
            "description": validated_data.get("description"),
            "item_type": validated_data.get("itemType", "movingfeature"),
            "update_frequency": validated_data.get("updateFrequency")
        }

        return collection_id, collection_data

    except Exception:
        connection.rollback()
        raise