# REQ6: /req/mf-collection/collection-get
# REQU 9: /req/mf-collection/collection-get-success
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas.collection import Collection
from resource.collection.collection_helper import (
    build_collection_response,
)

async def get_collection_id(session: AsyncSession,collection_id: str,  base_url: str):
    try:
        collection = await session.get(Collection,collection_id)
        if collection is None:
            raise ValueError(
                f"Collection '{collection_id}' not found"
            )
        if not collection:
            raise ValueError(f"Collection '{collection_id}' not found")
        
        result = await session.execute(
        text(
            """
            SELECT
                extent(tg.trajectory) AS extent,
                extent(tg.trajectory)::tstzspan AS extent_period,

                (
                    SELECT mf.crs
                    FROM moving_features mf
                    WHERE mf.collection_id = :collection_id
                    LIMIT 1
                ) AS crs,

                (
                    SELECT mf.trs
                    FROM moving_features mf
                    WHERE mf.collection_id = :collection_id
                    LIMIT 1
                ) AS trs

            FROM temporal_geometries tg
            WHERE tg.collection_id = :collection_id
            """
        ),
        {"collection_id": collection_id},
    )

        derived = result.mappings().first()


        collection_data = {
            "id": collection.id,
            "title": collection.title,
            "description": collection.description,
            "update_frequency": collection.update_frequency,
            "item_type": collection.item_type,

            "extent": (
                derived["extent"]
                if derived
                else None
            ),
            "extent_period": (
                derived["extent_period"]
                if derived
                else None
            ),
            "crs": (
                derived["crs"]
                if derived
                else None
            ),

            "trs": (
                derived["trs"]
                if derived
                else None
            ),
        }

        return build_collection_response(collection_data, base_url)


    except Exception:
        raise