# REQ20: /req/movingfeatures/mf-delete
# REQ22: /req/movingfeatures/mf-delete-success
from psycopg2 import sql
from fastapi import HTTPException, Response


def delete_single_moving_feature(
    collection_id: str,
    feature_id: str,
    connection,
    cursor
):
    conn = connection

    try:
        # Check collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        # Delete feature
        cursor.execute(
            """
            DELETE FROM moving_features
            WHERE id = %s AND collection_id = %s
            RETURNING id
            """,
            (feature_id, collection_id),
        )

        deleted = cursor.fetchone()

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )

        conn.commit()

        # Req22 → 204 No Content
        return Response(status_code=204)

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )