# REQ 8: /req/mf-collection/collection-delete
# REQU11: /req/mf-collection/collection-delete-success

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from db.schemas.collection import Collection
async def delete_collection(collection_id, session):
    try:



        # check collection exists
        collection = await session.get(
            Collection,
            collection_id,
        )

        if not collection:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        # delete
        await session.delete(collection)
        await session.commit()
      
        return None

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))