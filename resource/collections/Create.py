# REQ 2: /req/mf-collection/collections-post
# REQ 4: /req/mf-collection/collections-post-success

from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas.collection import Collection

async def post_collections(session: AsyncSession,data_dict: dict,base_url: str):
    try:
        # Attribute data validation
        validated_data = data_dict.copy()

        collection_id = (
            validated_data["title"]
            .lower()
            .replace(" ", "_")
        )

        # check existence
        existing_collection = await session.get(Collection,
            collection_id,
        )

        if existing_collection is not None:
            raise ValueError(
                f'Collection "{validated_data.get("title")}" already exists.'
            )

        collection = Collection(
            id=collection_id,
            title=validated_data["title"],
            description=validated_data.get("description"),
            update_frequency=validated_data.get("updateFrequency"),
            item_type=validated_data.get(
                "itemType",
                "movingfeature",
            ),
        )

        session.add(collection)
        await session.commit()


        collection_data = {
            "id": collection_id,
            "title": validated_data.get("title"),
            "description": validated_data.get("description"),
            "item_type": validated_data.get("itemType", "movingfeature"),
            "update_frequency": validated_data.get("updateFrequency")
        }

        return collection_id, collection_data

    except Exception:
        await session.rollback()
        raise