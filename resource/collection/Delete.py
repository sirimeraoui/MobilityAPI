# REQ 8: /req/mf-collection/collection-delete
# REQU11: /req/mf-collection/collection-delete-success


from fastapi import HTTPException
from db.schemas.collection import Collection
async def delete_collection(collection_id, backend):

    # check collection exists
    collection = await backend.delete(collection_id)

    if not collection:
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_id}' not found"
        )

    return None