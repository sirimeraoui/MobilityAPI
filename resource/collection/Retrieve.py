# REQ6: /req/mf-collection/collection-get
# REQU 9: /req/mf-collection/collection-get-success
from resource.collection.collection_helper import (
    build_collection_response,
)


async def get_collection_id(
    backend,
    collection_id: str,
    base_url: str,
):
    collection = await backend.get(collection_id)

    if collection is None:
        raise ValueError(
            f"Collection '{collection_id}' not found"
        )

    return build_collection_response(
        collection,
        base_url,
    )