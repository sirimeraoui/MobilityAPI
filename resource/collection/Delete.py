# REQ 8: /req/mf-collection/collection-delete
# REQU11: /req/mf-collection/collection-delete-success

from fastapi import HTTPException

def delete_collection(collection_id, connection, cursor):
    try:
        # check table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'collections'
            )
        """)

        table_exists = cursor.fetchone()[0]

        if not table_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        # check collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        # delete
        cursor.execute(
            "DELETE FROM collections WHERE id = %s",
            (collection_id,)
        )

        connection.commit()

        # FastAPI way: return nothing for 204
        return None

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))