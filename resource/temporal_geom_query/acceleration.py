# REQ 32: /req/movingfeatures/tpgeometry-query
# REQ 33: /req/movingfeatures/tpgeometry-query-success
# SECTION 8.7.5. Acceleration Query 

from resource.temporal_geom_query.query_helper import build_query_response
from fastapi import HTTPException
import traceback
import traceback

#GET /collections/{collectionId}/items/{featureId}/tgsequence/{geometryId}/acceleration
async def get_acceleration(
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
            (feature_id, collection_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )


        #temp geom exists for feature 
        cursor.execute(
            """
            SELECT id 
            FROM temporal_geometries 
            WHERE id = %s 
            AND feature_id = %s 
            AND collection_id = %s
            """,
            (geometry_id, feature_id, collection_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Temporal geometry '{geometry_id}' not found for feature '{feature_id}'"
            )


        cursor.execute(
            """
            SELECT 
                getTimestamp(unnest(instants(speed(trajectory)))) as time,
                getValue(unnest(instants(speed(trajectory)))) as speed
            FROM temporal_geometries
            WHERE id = %s 
            AND feature_id = %s 
            AND collection_id = %s
            """,
            (
                geometry_id,
                feature_id,
                collection_id
            )
        )

        rows = cursor.fetchall()


        #remark: speed returns stepwise interpolation, derivative requires LInear, 
        #toLinear() doesn't accept tfloat type , for now python compute the derivative clean check


        if len(rows) < 2:
            raise HTTPException(
                status_code=404,
                detail="Not enough speed data points for acceleration"
            )


        #ACCELERATION between each pair of points (tfloats)
        datetimes = []
        acceleration_values = []


        for i in range(len(rows) - 1):

            t1, s1 = rows[i]
            t2, s2 = rows[i + 1]

            dt = (t2 - t1).total_seconds()

            if dt > 0:
                accel = (s2 - s1) / dt

                datetimes.append(
                    t2.isoformat()
                    if hasattr(t2, "isoformat")
                    else str(t2)
                )

                acceleration_values.append(float(accel))


        # optional first point = 0
        datetimes.insert(
            0,
            rows[0][0].isoformat()
            if hasattr(rows[0][0], "isoformat")
            else str(rows[0][0])
        )

        acceleration_values.insert(0, 0.0)


        values = {
            "datetimes": datetimes,
            "values": acceleration_values
        }


        #acc first point to 0

        if not values:
            raise HTTPException(
                status_code=404,
                detail="No acceleration data found"
            )


        # response
        path = (
            f"/collections/{collection_id}/items/"
            f"{feature_id}/tgsequence/{geometry_id}/acceleration"
        )


        response = build_query_response(
            values=values,
            unit="m/s²",
            query_type="acceleration",
            base_url="",
            path=path
        )


        return response


    except HTTPException:
        raise


    except Exception as e:
        connection.rollback()

        print(f"Error in acceleration query: {e}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )