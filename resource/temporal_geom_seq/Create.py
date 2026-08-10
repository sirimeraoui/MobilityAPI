# REQ 26: /req/movingfeatures/tgsequence-post
# REQ 28: /req/movingfeatures/tgsequence-post-success
import json
from fastapi import HTTPException, Response
import re
import traceback


# POST base/collections/{collectionId}/items/{featureId}/tgsequence
async def post_tgsequence(
    collection_id: str,
    feature_id: str,
    response: Response,
    connection,
    cursor,
    data: dict
):

    try:
        # collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id=%s",
            (collection_id,),
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

        # SRID
        cursor.execute(
            """
            SELECT crs
            FROM moving_features
            WHERE id=%s
              AND collection_id=%s
            """,
            (feature_id, collection_id),
        )

        crs = cursor.fetchone()

        match = re.search(r"(\d+)", str(crs[0]["properties"]))
        srid = int(match.group(1))

        tgeom_mfjson = json.dumps(data)

        columns = [
            "feature_id",
            "collection_id",
            "geometry_type",
            "geometry",
            "trajectory",
            "interpolation",
        ]

        placeholders = [
            "%s",
            "%s",
            "%s",
            "trajectory(SETSRID(tgeompointFromMFJSON(%s), %s))",
            "SETSRID(tgeompointFromMFJSON(%s), %s)",
            "%s",
        ]

        values = [
            feature_id,
            collection_id,
            data.get("type", "MovingPoint"),
            tgeom_mfjson,
            srid,
            tgeom_mfjson,
            srid,
            data.get("interpolation", "Linear"),
        ]

        if data.get("base") is not None:
            columns.append("base")
            placeholders.append("%s")
            values.append(data["base"])

        if data.get("orientations") is not None:
            columns.append("orientations")
            placeholders.append("%s")
            values.append(data["orientations"])

        query = f"""
            INSERT INTO temporal_geometries
            ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
            RETURNING id
        """

        cursor.execute(query, values)

        new_id = cursor.fetchone()[0]

        connection.commit()

        response.headers[
            "Location"
        ] = f"/collections/{collection_id}/items/{feature_id}/tgsequence/{new_id}"

        return data

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