# REQ42: /req/movingfeatures/tproperty-post
# REQ45: /req/movingfeatures/tproperty-post-success
# REQ 47: /req/movingfeatures/tpvalue-mandatory

import json
import traceback

from datetime import datetime
from fastapi import HTTPException

from resource.temporal_properties.property_helper import validate_interpolation
from resource.temporal_properties.validation_helper import (
    validate_value_data,
    validate_collection_exists,
    validate_feature_exists,
    validate_property_exists,
    validate_temporal_continuity,
)


# POST /collections/{collectionId}/items/{featureId}/tproperties/{propertyName}
# temporal_values table
# rename to post temporal property value, misleading, check clean
async def post_temporal_property(
    collection_id: str,
    feature_id: str,
    property_name: str,
    data: dict,
    db,
):
    connection, cursor = db

    try:
        # Validate
        errors = validate_value_data(data)
        if errors:
            raise HTTPException(
                status_code=400,
                detail="; ".join(errors),
            )

        # Acceptable interpolation values?
        if (
            "interpolation" in data
            and not validate_interpolation(data["interpolation"])
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid interpolation: {data['interpolation']}",
            )

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

        # property exists?
        prop_row = validate_property_exists(
            cursor,
            feature_id,
            property_name,
        )

        if prop_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Property '{property_name}' not found for feature '{feature_id}'",
            )

        property_id = prop_row[0]

        # New values must start after existing data (last time::
        first_new_time = datetime.fromisoformat(
            data["datetimes"][0].replace("Z", "+00:00")
        )

        is_valid, last_time = validate_temporal_continuity(
            cursor,
            property_id,
            first_new_time,
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"New values must start after existing data (last time: {last_time.isoformat()})",
            )

        # datetimes----> pgsql acceptable timestamp format
        # Note: pgsql expects timestamps without 'Z' and with space instead of 'T'
        pg_datetimes = []

        for dt_str in data["datetimes"]:
            pg_dt = dt_str.replace("T", " ").replace("Z", "+00")
            pg_datetimes.append(pg_dt)

        # INSERT INTO temporal_values:
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
                json.dumps(data["values"]),  # jsonb
                data.get("interpolation", "Linear"),
            ),
        )

        new_id = cursor.fetchone()[0]

        connection.commit()

        # 201
        # re check content clean
        return {
            "message": "Values added successfully",
            "id": new_id,
        }

    except HTTPException:
        raise

    except Exception as e:
        connection.rollback()
        print(f"Error in post_temporal_property: {e}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )