# REQ7: /req/mf-collection/collection-put
# RE10: /req/mf-collection/collection-put-success
import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas.collection import Collection
from datetime import datetime, timezone



async def put_collection(collection_id, data_dict, session: AsyncSession):
    try:
        # Check if collection exists
        collection = await session.get(
            Collection,
            collection_id,
        )
        if collection is None:
            raise ValueError(
                f"Collection '{collection_id}' not found"
            )

        # update DB
        if "title" in data_dict:
            collection.title = data_dict["title"]

        if "description" in data_dict:
            collection.description = data_dict["description"]

        if "itemType" in data_dict:
            collection.item_type = data_dict["itemType"]

        collection.updated_at = datetime.utcnow()
        await session.commit()

        return True

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    except Exception as e:
        await session.rollback()
        raise 