# REQ 37: /req/movingfeatures/tproperties-post
# REQ 39: /req/movingfeatures/tproperties-post-success
# REQ 40: /req/movingfeatures/tproperty-mandatory

from fastapi import HTTPException
from resource.temporal_properties.property_helper import validate_property_type
from resource.temporal_properties.validation_helper import (
    validate_property_data,
    validate_collection_exists,
    validate_feature_exists,
)
import traceback
import json


# POST /collections/{collectionId}/items/{featureId}/tproperties
async def post_tproperties(
    collection_id: str,
    feature_id: str,
    data: dict,
    db,
):
    connection, cursor = db

    try:

        # collection exists
        if not validate_collection_exists(cursor, collection_id):
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        # feature exists
        if not validate_feature_exists(cursor, feature_id, collection_id):
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'",
            )

        if data.get("name") is not None:

            # Validate required fields
            errors = validate_property_data(data)
            if errors:
                raise HTTPException(
                    status_code=400,
                    detail="; ".join(errors),
                )

            # Validate property type- REQ 40
            if not validate_property_type(data["type"]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid property type: {data['type']}. Must be one of: TBoolean, TText, TInteger, TReal, TImage",
                )

            # property already exists with same name?
            cursor.execute(
                """
                SELECT id
                FROM temporal_properties
                WHERE feature_id = %s
                  AND property_name = %s
                """,
                (feature_id, data["name"]),
            )

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail=f"Property '{data['name']}' already exists for this feature",
                )

            # otherwise, INSERT INTO temporal_properties
            cursor.execute(
                """
                INSERT INTO temporal_properties
                (feature_id, property_name, property_type, form, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    feature_id,
                    data["name"],
                    data["type"],
                    data.get("form"),
                    data.get("description", ""),
                ),
            )

            new_id = cursor.fetchone()[0]
            connection.commit()

            return {
                "message": "Temporal property created successfully",
                "id": new_id,
                "location": f"/collections/{collection_id}/items/{feature_id}/tproperties/{data['name']}",
            }

        elif data.get("datetimes") is not None and data.get("name") is None:

            # with values
            datetimes = data["datetimes"]

            property_name = None
            for key, value in data.items():
                if key != "datetimes":
                    property_name = key
                    data = value
                    break

            # Validate property type- REQ 40
            if not validate_property_type(data["type"]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid property type: {data['type']}. Must be one of: TBoolean, TText, TInteger, TReal, TImage",
                )

            cursor.execute(
                """
                SELECT id
                FROM temporal_properties
                WHERE feature_id = %s
                  AND property_name = %s
                """,
                (feature_id, property_name),
            )

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail=f"Property '{property_name}' already exists for this feature",
                )

            cursor.execute(
                """
                INSERT INTO temporal_properties
                (feature_id, property_name, property_type, form, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    feature_id,
                    property_name,
                    data["type"],
                    data.get("form"),
                    data.get("description", ""),
                ),
            )

            property_id = cursor.fetchone()[0]
            connection.commit()

            pg_datetimes = []
            for dt_str in datetimes:
                pg_dt = dt_str.replace("T", " ").replace("Z", "+00")
                pg_datetimes.append(pg_dt)

            cursor.execute(
                """
                INSERT INTO temporal_values
                (property_id, datetimes, values, interpolation)
                VALUES (%s, %s::timestamptz[], %s, %s)
                RETURNING id
                """,
                (
                    property_id,
                    pg_datetimes,
                    json.dumps(data["values"]),
                    data.get("interpolation", "Linear"),
                ),
            )

            new_id = cursor.fetchone()[0]
            connection.commit()

            return {
                "message": "Temporal property with values created successfully",
                "id": new_id,
                "location": f"/collections/{collection_id}/items/{feature_id}/tproperties/{property_name}",
            }

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid temporal property payload",
            )

    except HTTPException:
        raise

    except Exception as e:
        connection.rollback()
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )