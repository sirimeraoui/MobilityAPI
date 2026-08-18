from db.schemas.collection import Collection
from backends.base.collections import CollectionsBackend
from sqlalchemy import text
from datetime import datetime, timezone

class MobilityDBCollectionsBackend(CollectionsBackend):

    def __init__(self, session):
        self.session = session

    async def exists(self, collection_id: str):
        collection = await self.session.get(
            Collection,
            collection_id,
        )

        return collection is not None

    async def fetch_all_collections(self):
        result = await self.session.execute(
            text("""
                SELECT
                    c.id,
                    c.title,
                    c.description,
                    c.update_frequency,
                    c.item_type,

                    extent(tg.trajectory) AS extent,
                    extent(tg.trajectory)::tstzspan AS extent_period,

                    (
                        SELECT mf.crs
                        FROM moving_features mf
                        WHERE mf.collection_id = c.id
                        LIMIT 1
                    ) AS crs,

                    (
                        SELECT mf.trs
                        FROM moving_features mf
                        WHERE mf.collection_id = c.id
                        LIMIT 1
                    ) AS trs

                FROM collections c

                LEFT JOIN temporal_geometries tg
                    ON tg.collection_id = c.id

                GROUP BY c.id, c.title

                ORDER BY c.created_at DESC
            """)
        )

        return result.mappings().all()

    async def create(self, data: dict):
        collection = Collection(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            update_frequency=data.get("update_frequency"),
            item_type=data.get("item_type", "movingfeature"),
        )

        self.session.add(collection)
        await self.session.commit()
        return collection



    # by id one collection-----------------------------------
    async def get(self, collection_id: str):
        result = await self.session.execute(
            text("""
                SELECT
                    c.id,
                    c.title,
                    c.description,
                    c.update_frequency,
                    c.item_type,

                    extent(tg.trajectory) AS extent,
                    extent(tg.trajectory)::tstzspan AS extent_period,

                    (
                        SELECT mf.crs
                        FROM moving_features mf
                        WHERE mf.collection_id = c.id
                        LIMIT 1
                    ) AS crs,

                    (
                        SELECT mf.trs
                        FROM moving_features mf
                        WHERE mf.collection_id = c.id
                        LIMIT 1
                    ) AS trs

                FROM collections c

                LEFT JOIN temporal_geometries tg
                    ON tg.collection_id = c.id

                WHERE c.id = :collection_id

                GROUP BY
                    c.id,
                    c.title,
                    c.description,
                    c.update_frequency,
                    c.item_type
            """),
            {
                "collection_id": collection_id,
            },
        )

        return result.mappings().first()


    async def replace(self, collection_id: str, data: dict):
        collection = await self.session.get(
            Collection,
            collection_id,
        )

        if collection is None:
            return False

        if "title" in data:
            collection.title = data["title"]

        if "description" in data:
            collection.description = data["description"]

        if "itemType" in data:
            collection.item_type = data["itemType"]

        collection.updated_at = datetime.utcnow()

        try:
            await self.session.commit()
            return True

        except Exception:
            await self.session.rollback()
            raise



    async def delete(self, collection_id: str):
        collection = await self.session.get(
            Collection,
            collection_id,
        )

        if collection is None:
            return False

        try:
            await self.session.delete(collection)
            await self.session.commit()
            return True

        except Exception:
            await self.session.rollback()
            raise