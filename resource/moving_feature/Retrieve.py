# REQ 19: /req/movingfeatures/mf-get
# REQ 21: /req/movingfeatures/mf-get-success
from resource.moving_feature.feature_helper import build_feature_from_row
import traceback
from fastapi import HTTPException


async def get_movement_single_moving_feature(
    collection_id: str,
    feature_id: str,
    backend
):


    try:
        # Check collection exists
        if not await backend.collection_exists(collection_id):
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        await backend.begin()
        row = await backend.get_feature(collection_id, feature_id)

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )

        feature = build_feature_from_row(
            row,
            collection_id,
            include_temporal=True,
            single=True,
        )

        return feature

    except HTTPException:
        raise

    except Exception as e:
        await backend.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
            # trace= traceback.format_exc()
        )