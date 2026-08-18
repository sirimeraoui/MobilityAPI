# REQ 2: /req/mf-collection/collections-post
# REQ 4: /req/mf-collection/collections-post-success

from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas.collection import Collection

async def post_collections(
    backend,
    data_dict: dict,
    base_url: str,
):
    validated_data = data_dict.copy()

    collection_id = (
        validated_data["title"]
        .lower()
        .replace(" ", "_")
    )

    if await backend.exists(collection_id):
        raise ValueError(
            f'Collection "{validated_data.get("title")}" already exists.'
        )

    collection_data = {
        "id": collection_id,
        "title": validated_data["title"],
        "description": validated_data.get("description"),
        "update_frequency": validated_data.get("updateFrequency"),
        "item_type": validated_data.get(
            "itemType",
            "movingfeature",
        ),
    }

    await backend.create(collection_data)

    return collection_id, collection_data