# REQ 32: /req/movingfeatures/tpgeometry-query
# REQ 33: /req/movingfeatures/tpgeometry-query-success
# SECTION 8.7.4. Velocity Query

from fastapi import HTTPException
from resource.temporal_geom_query.query_helper import build_query_response
import traceback


#GET /collections/{collectionId}/items/{featureId}/tgsequence/{geometryId}/velocity
async def get_velocity(
    collection_id,
    feature_id,
    geometry_id,
    connection,
    cursor
):

    try:

        #collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )


        #feature exists
        cursor.execute(
            """
            SELECT id 
            FROM moving_features 
            WHERE id = %s 
            AND collection_id = %s
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


        #geometry exists for feature
        cursor.execute("""
            SELECT id 
            FROM temporal_geometries 
            WHERE id = %s 
            AND feature_id = %s 
            AND collection_id = %s
        """,
        (
            geometry_id,
            feature_id,
            collection_id
        ))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Temporal geometry '{geometry_id}' not found for feature '{feature_id}'"
            )


##############################################################################################################################

#speed
        cursor.execute("""
            SELECT 
                getTimestamp(
                    unnest(instants(speed(trajectory)))
                ) as time,
                getValue(
                    unnest(instants(speed(trajectory)))
                ) as speed
            FROM temporal_geometries
            WHERE id = %s 
            AND feature_id = %s 
            AND collection_id = %s
        """,
        (
            geometry_id,
            feature_id,
            collection_id
        ))


        rows = cursor.fetchall()


        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No velocity data found for geometry '{geometry_id}'"
            )


        values = {
            "datetimes": [
                t.isoformat() if hasattr(t, "isoformat") else str(t)
                for t, d in rows
            ],

            "values": [
                float(d)
                for t, d in rows
            ]
        }


        #response
        path = (
            f"/collections/{collection_id}/items/"
            f"{feature_id}/tgsequence/{geometry_id}/velocity"
        )


        response = build_query_response(
            values=values,
            unit="m/s",
            query_type="velocity",
            base_url="",
            path=path
        )


        return response


    except HTTPException:
        raise


    except Exception as e:
        connection.rollback()

        print(f"Error in velocity query: {e}", flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )