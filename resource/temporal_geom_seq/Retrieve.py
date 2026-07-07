# REQ 25: /req/movingfeatures/tgsequence-get
# REQ 27: /req/movingfeatures/tgsequence-get-success

from datetime import datetime
import json
from fastapi import HTTPException
import traceback

# GET base/collections/{collectionId}/items/{featureId}/tgsequence
async def get_tgsequence(
    collection_id: str,
    feature_id: str,
    connection, 
    cursor 
):
     
    try:
        # collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id=%s",
            (collection_id,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        # feature exists
        cursor.execute(
            """
            SELECT id
            FROM moving_features
            WHERE id=%s
              AND collection_id=%s
            """,
            (feature_id, collection_id),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found",
            )

        # temporal geometries
        cursor.execute(
            """
            SELECT
                id,
                geometry_type,
                asMFJSON(trajectory),
                interpolation,
                base
            FROM temporal_geometries
            WHERE feature_id=%s
              AND collection_id=%s
            ORDER BY id
            """,
            (feature_id, collection_id),
        )

        rows = cursor.fetchall()

        geometries = []

        for row in rows:
            traj = json.loads(row[2]) if row[2] else {}

            geometries.append({
                "id": row[0],
                "type": row[1],
                "datetimes": traj.get("datetimes", []),
                "coordinates": traj.get("coordinates", []),
                "interpolation": row[3],
                "base": row[4],
            })

        return {
            "type": "TemporalGeometrySequence",
            "geometrySequence": geometries,
            "links": [{
                "href": f"/collections/{collection_id}/items/{feature_id}/tgsequence",
                "rel": "self",
                "type": "application/json",
            }],
            "timeStamp": datetime.utcnow().isoformat() + "Z",
            "numberMatched": len(geometries),
            "numberReturned": len(geometries),
        }

    except HTTPException:
        raise

    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )