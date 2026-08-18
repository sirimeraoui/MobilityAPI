# REQ1: /req/mf-collection/collections-get
# REQ 3: /req/mf-collection/collections-get-success
from resource.collection.collection_helper import (

    build_collection_response,
    build_collections_list_response
)


async def get_collections(backend, base_url: str):
    try:

        collections_data = await backend.fetch_all_collections()

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



