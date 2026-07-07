# REQ 30: /req/movingfeatures/tpgeometry-delete
# REQ 31: /req/movingfeatures/tpgeometry-delete-success

from fastapi import HTTPException


# DELETE base/collections/{collectionId}/items/{featureId}/tgsequence/{geometryId}
def delete_single_temporal_primitive_geo(
    collection_id,
    feature_id,
    geometry_id,
    connection,
    cursor
):
    
    try:
        #---------------------------------collection && feature && geomerty exist ??---------------------------------------
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )


        #feature exists?
        # addition 14/03 clean
        cursor.execute(
            "SELECT id FROM moving_features WHERE id = %s AND collection_id = %s",
            (feature_id, collection_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found"
            )


        # geometry exists (by collection by mf) 
        cursor.execute("""
            SELECT tg.id 
            FROM temporal_geometries tg
            JOIN moving_features mf ON tg.feature_id = mf.id
            WHERE tg.id = %s 
              AND mf.id = %s 
              AND mf.collection_id = %s
        """, (geometry_id, feature_id, collection_id))
        

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Temporal geometry {geometry_id} not found"
            )


        #----------------------------------------------------------------------------------------------------------------------
        # delete
        cursor.execute(
            """DELETE FROM temporal_geometries
            WHERE id = %s
              AND feature_id = %s
              AND collection_id = %s
            """,
            (geometry_id, feature_id, collection_id)
        )
        
        connection.commit()
        
        # response Req 31)
        # FastAPI router handles the 204 response
        return None


    except HTTPException:
        raise


    except Exception as e:
        connection.rollback()
        print(f"Error in delete_single_temporal_primitive_geo: {e}", flush=True)

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )