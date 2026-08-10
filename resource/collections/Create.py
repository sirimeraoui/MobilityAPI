# REQ 2: /req/mf-collection/collections-post
# REQ 4: /req/mf-collection/collections-post-success

from resource.collection.collection_helper import (
    collection_exists,
    insert_collection
)

def post_collections(connection, cursor, data_dict, base_url):
    try:
        # Attribute data validation
        validated_data = data_dict.copy()

        collection_id = (
            validated_data["title"]
            .lower()
            .replace(" ", "_")
        )

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