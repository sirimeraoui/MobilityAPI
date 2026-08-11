# REQ 26: /req/movingfeatures/tgsequence-post
# REQ 28: /req/movingfeatures/tgsequence-post-success
import json
from fastapi import HTTPException, Response
import re
import traceback
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas.collection import Collection

# POST base/collections/{collectionId}/items/{featureId}/tgsequence
async def post_tgsequence(
    collection_id: str,
    feature_id: str,
    response: Response,
    session:AsyncSession,
    data: dict
):

    try:
        # collection exists
        collection = await session.get(Collection,collection_id)

        if collection is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        # feature exists + get CRS
        result = await session.execute(
            text("""
                SELECT id, crs
                FROM moving_features
                WHERE id = :feature_id
                  AND collection_id = :collection_id
            """),
            {
                "feature_id": feature_id,
                "collection_id": collection_id,
            },
        )

        feature = result.mappings().first()

        if feature is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found",
            )


        crs = feature["crs"]
        srid = 4326
        if crs:
            match = re.search(r"(\d+)",str(crs.get("properties", "")))

            if match:
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
            ":feature_id",
            ":collection_id",
            ":geometry_type",
            "trajectory(SETSRID(tgeompointFromMFJSON(:mfjson), :srid))",
            "SETSRID(tgeompointFromMFJSON(:mfjson), :srid)",
            ":interpolation",
        ]

        values = {
            "feature_id": feature_id,
            "collection_id": collection_id,
            "geometry_type": data.get("type", "MovingPoint"),
            "mfjson": tgeom_mfjson,
            "srid": srid,
            "interpolation": data.get("interpolation", "Linear"),
        }

        if data.get("base") is not None:
            columns.append("base")
            placeholders.append(":base")
            values["base"] = json.dumps(data["base"])


        if data.get("orientations") is not None:
            columns.append("orientations")
            placeholders.append(":orientations")
            values["orientations"] = json.dumps(
                data["orientations"]
            )

        query = f"""
            INSERT INTO temporal_geometries
            ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
            RETURNING id
        """

        result = await session.execute(
        text(query),
        values,
        )


        new_id = result.scalar_one()

        await session.commit()

        response.headers[
            "Location"
        ] = f"/collections/{collection_id}/items/{feature_id}/tgsequence/{new_id}"

        return data

    except HTTPException:
        await session.rollback()
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