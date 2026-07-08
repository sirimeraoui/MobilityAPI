# REQ43: /req/movingfeatures/tproperty-delete
# REQ46: /req/movingfeatures/tproperty-delete-success

from fastapi import HTTPException
import traceback


# DELETE /collections/{collectionId}/items/{featureId}/tproperties/{propertyName}
def delete_temporal_property(
    collection_id,
    feature_id,
    property_name,
    connection,
    cursor
):
    try:

        # collection exists
        cursor.execute(
            """
            SELECT id 
            FROM collections 
            WHERE id=%s
            """,
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
            WHERE id=%s
              AND collection_id=%s
            """,
            (
                feature_id,
                collection_id
            )
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )


        # delete property
        # ON DELETE CASCADE removes temporal_values
        cursor.execute(
            """
            DELETE FROM temporal_properties
            WHERE feature_id=%s
              AND property_name=%s
            RETURNING id
            """,
            (
                feature_id,
                property_name
            )
        )


        deleted = cursor.fetchone()


        if deleted is None:
            raise HTTPException(
                status_code=404,
                detail=f"Property '{property_name}' not found for feature '{feature_id}'"
            )


        connection.commit()


        # FastAPI automatically creates 204 response
        return None


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