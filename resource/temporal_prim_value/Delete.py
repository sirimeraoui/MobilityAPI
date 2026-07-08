# REQ 48: /req/movingfeatures/tpvalue-delete
# REQ 49: /req/movingfeatures/tpvalue-delete-success

from fastapi import HTTPException
import traceback


# DELETE /collections/{collectionId}/items/{featureId}/tproperties/{propertyName}/{valueId}
def delete_temporal_primitive_value(
    collection_id,
    feature_id,
    property_name,
    value_id,
    connection,
    cursor
):

    try:

        # collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )


        # feature exists
        cursor.execute(
            """
            SELECT id
            FROM moving_features
            WHERE id = %s
              AND collection_id = %s
            """,
            (feature_id, collection_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )


        # Get property id
        cursor.execute(
            """
            SELECT id
            FROM temporal_properties
            WHERE feature_id = %s
              AND property_name = %s
            """,
            (feature_id, property_name)
        )

        prop_row = cursor.fetchone()

        if prop_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Property '{property_name}' not found for feature '{feature_id}'"
            )


        property_id = prop_row[0]


        # DELETE temporal value
        cursor.execute(
            """
            DELETE FROM temporal_values
            WHERE id = %s
              AND property_id = %s
            RETURNING id
            """,
            (value_id, property_id)
        )


        deleted = cursor.fetchone()

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Value '{value_id}' not found for property '{property_name}'"
            )


        connection.commit()

        return None   # FastAPI will return 204


    except HTTPException:
        raise


    except Exception as e:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )