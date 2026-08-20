# REQ15: /req/movingfeatures/features-post
# REQ 17: /req/movingfeatures/features-post-success
import uuid
import json
import re
import traceback
from sqlalchemy import insert, func, text

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from zmq import backend


from db.schemas.temporal_geometry import TemporalGeometry


async def post_collection_items(
    collection_id: str,
    data: dict,
    backend,
    base_url: str
):
    try:
        # Check collection exists
        if not await backend.collection_exists(collection_id) :
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        created_feature_ids = []

        if data["type"] == "FeatureCollection":
            features = data["features"]
        else:
            features = [data]

        await backend.begin()

        for feature in features:
            feature_id = await backend.create(feature=feature,collection_id=collection_id)
            if feature_id:
                created_feature_ids.append(feature_id)
                
        await backend.commit()
        locations = ", ".join(
            f"{base_url}api/v1/collections/{collection_id}/items/{feature_id}"
            for feature_id in created_feature_ids
        )
        # print(repr(locations))
        return JSONResponse(
            status_code=201,
            content={
                "message": f"Created {len(created_feature_ids)} features",
                "ids": created_feature_ids,
            },
            headers={
                "Location": locations,
            },
        )

    except HTTPException:
        await backend.rollback()
        raise

    except Exception as e:
        await backend.rollback()
        traceback.print_exc()
        msg = str(e)

        if "duplicate" in msg.lower():
            raise HTTPException(
                status_code=409,
                detail=msg,
            )

        raise HTTPException(
            status_code=500,
            detail=msg,
        )
