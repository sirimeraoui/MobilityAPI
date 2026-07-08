# REQ 41: /req/movingfeatures/tproperty-get
# REQU 44: /req/movingfeatures/tproperty-get-success

from fastapi import HTTPException
import traceback


# GET /collections/{collectionId}/items/{featureId}/tproperties/{propertyName}
async def get_temporal_property(
    collection_id: str,
    feature_id: str,
    property_name: str,
    datetime_param: str | None = None,
    subTemporalValue: bool = False,
    db=None,
):
    connection, cursor = db

    try:

        # Parse datetime (Req52)
        dt1 = dt2 = None
        if datetime_param:
            if "/" in datetime_param:
                dt1, dt2 = datetime_param.split("/")
                # subTrajectory== true==> bounder interval (Req 12C)
                if subTemporalValue and (not dt1 or not dt2):
                    raise HTTPException(
                        status_code=400,
                        detail="subTemporalValue requires a bounded datetime interval",
                    )
            else:
                dt1 = datetime_param
                if subTemporalValue:
                    raise HTTPException(
                        status_code=400,
                        detail="subTemporalValue requires a bounded interval, not a single instant",
                    )

        # subTrajectory without datetime interval code 400
        if subTemporalValue and not (dt1 and dt2):
            raise HTTPException(
                status_code=400,
                detail="subTemporalValue requires a datetime interval",
            )

        # collection && feature exist:+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        cursor.execute(
            """
            SELECT id
            FROM moving_features
            WHERE id = %s
              AND collection_id = %s
            """,
            (feature_id, collection_id),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'",
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

        prop_row = cursor.fetchone()

        if prop_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Property '{property_name}' not found for feature '{feature_id}'",
            )

        property_id = prop_row[0]

        temporal_properties = []

        if dt1 and dt2:

            if subTemporalValue:

                query = """
                    SELECT
                        array_agg(d.t ORDER BY d.idx) AS datetimes,
                        array_agg(v.val::float ORDER BY d.idx) AS values,
                        tv.interpolation
                    FROM temporal_values tv
                    CROSS JOIN LATERAL unnest(tv.datetimes) WITH ORDINALITY AS d(t, idx)
                    CROSS JOIN LATERAL jsonb_array_elements_text(tv.values) WITH ORDINALITY AS v(val, idx2)
                    WHERE tv.property_id = %s
                      AND d.idx = v.idx2
                      AND d.t >= %s
                      AND d.t <= %s
                    GROUP BY tv.interpolation
                """

                cursor.execute(query, (property_id, dt1, dt2))

                row = cursor.fetchone()

                if row and row[0]:
                    temporal_properties.append({
                        "datetimes": [
                            dt.isoformat() if hasattr(dt, "isoformat") else dt
                            for dt in row[0]
                        ],
                        "values": row[1],
                        "interpolation": row[2] or "Linear",
                    })

            else:

                query = """
                    SELECT
                        tv.datetimes,
                        tv.values,
                        tv.interpolation
                    FROM temporal_values tv
                    CROSS JOIN LATERAL unnest(tv.datetimes) AS d(t)
                    WHERE tv.property_id = %s
                      AND d.t >= %s
                      AND d.t <= %s
                    ORDER BY tv.datetimes[1]
                """

                cursor.execute(query, (property_id, dt1, dt2))

                rows = cursor.fetchall()

                for row in rows:
                    temporal_properties.append({
                        "datetimes": [
                            dt.isoformat() if hasattr(dt, "isoformat") else dt
                            for dt in row[0]
                        ],
                        "values": row[1],
                        "interpolation": row[2] or "Linear",
                    })

        else:

            cursor.execute(
                """
                SELECT
                    datetimes,
                    values,
                    interpolation
                FROM temporal_values
                WHERE property_id = %s
                ORDER BY datetimes[1]
                """,
                (property_id,),
            )

            rows = cursor.fetchall()

            for row in rows:
                temporal_properties.append({
                    "datetimes": [
                        dt.isoformat() if hasattr(dt, "isoformat") else dt
                        for dt in row[0]
                    ],
                    "values": row[1],
                    "interpolation": row[2] or "Linear",
                })

        path = f"/collections/{collection_id}/items/{feature_id}/tproperties/{property_name}"

        response = {
            "temporalProperties": temporal_properties,
            "links": [
                {
                    "href": path,
                    "rel": "self",
                    "type": "application/json",
                }
            ],
        }

        return response

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