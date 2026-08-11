# REQ 25: /req/movingfeatures/tgsequence-get
# REQ 27: /req/movingfeatures/tgsequence-get-success

from datetime import datetime
import json
from fastapi import HTTPException
import traceback
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas.collection import Collection
# GET base/collections/{collectionId}/items/{featureId}/tgsequence
async def get_tgsequence(
    collection_id: str,
    feature_id: str,
    session: AsyncSession
):
     
    try:
        # collection exists
        collection = await session.get(Collection,collection_id)

        if collection is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        # feature exists
        result = await session.execute(
        text("""
            SELECT id
            FROM moving_features
            WHERE id = :feature_id
                AND collection_id = :collection_id
        """),
            {
                "feature_id": feature_id,
                "collection_id": collection_id,
            },
        )

        if result.first() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found",
            )

        # temporal geometries
        result = await session.execute(
            text("""
                SELECT
                    id,
                    geometry_type,
                    asMFJSON(trajectory) AS trajectory,
                    interpolation,
                    base
                FROM temporal_geometries
                WHERE feature_id = :feature_id
                  AND collection_id = :collection_id
                ORDER BY id
            """),
            {
                "feature_id": feature_id,
                "collection_id": collection_id,
            },
        )

        rows = result.mappings().all()

        geometries = []

        for row in rows:
            traj = (
                json.loads(row["trajectory"])
                if row["trajectory"]
                else {}
            )

            geometries.append({
                "id": row["id"],
                "type": row["geometry_type"],
                "datetimes": traj.get("datetimes", []),
                "coordinates": traj.get("coordinates", []),
                "interpolation": row["interpolation"],
                "base": row["base"],
            })

        return {
            "type": "TemporalGeometrySequence",
            "geometrySequence": geometries,
            "links": [
                {
                    "href": (
                        f"/collections/{collection_id}/items/"
                        f"{feature_id}/tgsequence"
                    ),
                    "rel": "self",
                    "type": "application/json",
                }
            ],
            "timeStamp": datetime.utcnow().isoformat() + "Z",
            "numberMatched": len(geometries),
            "numberReturned": len(geometries),
        }

    except HTTPException:
        raise

    except Exception as e:
        await session.rollback()
        raise HTTPException( 
            status_code=500,
            detail={
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )