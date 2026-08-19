import duckdb

from backends.base.collections import CollectionsBackend

class MobilityDuckCollectionsBackend(CollectionsBackend):

    def __init__(self, connection):
        self.connection = connection
    async def exists(self, collection_id: str):
        row = self.connection.execute(
            """
            SELECT 1
            FROM collections
            WHERE id = ?
            LIMIT 1
            """,
            [collection_id],
        ).fetchone()
        return row is not None
# cl
    async def fetch_all_collections(self):
        rows = self.connection.execute(
            """
            SELECT
                id,
                title,
                description,
                update_frequency,
                item_type,
                NULL AS extent,
                NULL AS extent_period,
                NULL AS crs,
                NULL AS trs
            FROM collections
            ORDER BY created_at DESC
            """
        ).fetchall()

        columns = [
            "id",
            "title",
            "description",
            "update_frequency",
            "item_type",
            "extent",
            "extent_period",
            "crs",
            "trs",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    async def get(self, collection_id: str):
        row = self.connection.execute(
            """
            SELECT
                id,
                title,
                description,
                update_frequency,
                item_type,
                NULL AS extent,
                NULL AS extent_period,
                NULL AS crs,
                NULL AS trs
            FROM collections
            WHERE id = ?
            """,
            [collection_id],
        ).fetchone()

        if row is None:
            return None

        columns = [
            "id",
            "title",
            "description",
            "update_frequency",
            "item_type",
            "extent",
            "extent_period",
            "crs",
            "trs",
        ]

        return dict(zip(columns, row))

    async def create(self, data: dict):
        self.connection.execute(
            """
            INSERT INTO collections (
                id,
                title,
                description,
                update_frequency,
                item_type
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                data["id"],
                data["title"],
                data.get("description"),
                data.get("update_frequency"),
                data.get("item_type", "movingfeature"),
            ],
        )

        return True

    async def replace(
        self,
        collection_id: str,
        data: dict,
    ):
        if not await self.exists(collection_id):
            return False

        updates = []
        values = []

        if "title" in data:
            updates.append("title = ?")
            values.append(data["title"])

        if "description" in data:
            updates.append("description = ?")
            values.append(data["description"])

        if "itemType" in data:
            updates.append("item_type = ?")
            values.append(data["itemType"])

        if not updates:
            return True

        updates.append("updated_at = CURRENT_TIMESTAMP")

        values.append(collection_id)

        self.connection.execute(
            f"""
            UPDATE collections
            SET {", ".join(updates)}
            WHERE id = ?
            """,
            values,
        )

        return True

    async def delete(self, collection_id: str):
        if not await self.exists(collection_id):
            return False

        self.connection.execute(
            """
            DELETE FROM collections
            WHERE id = ?
            """,
            [collection_id],
        )

        return True