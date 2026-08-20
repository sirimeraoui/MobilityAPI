# REQ20: /req/movingfeatures/mf-delete
# REQ22: /req/movingfeatures/mf-delete-success
from psycopg2 import sql
from fastapi import HTTPException, Response
import traceback
async def delete_single_moving_feature(
    collection_id: str,
    feature_id: str,
    backend):
    try:
        # Check collection exists

        if not await backend.collection_exists(collection_id):
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found")

        # Delete feature
        deleted = await backend.delete(collection_id, feature_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )

        await backend.commit()
        # Req22 → 204 No Content
        return Response(status_code=204)

    except HTTPException:
        await backend.rollback()
        raise

    except Exception as e:
        await backend.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )