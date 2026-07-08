# REQ36: /req/movingfeatures/tproperties-get
# REQ38: /req/movingfeatures/tproperties-get-success
from resource.temporal_properties.property_helper import build_properties_list_response
import traceback
from fastapi import HTTPException

# GET properties  base/collections/{collectionId}/items/{featureId}/tproperties
async def get_tproperties(
    collection_id: str,
    feature_id: str,
    limit: int = 10,
    datetime_param: str | None = None,
    subTemporalValue: bool = False,
    db=None,
):
    connection, cursor = db

    try:

        # Req 50: max 10000
        limit = min(limit, 10000)

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
                dt1 = datetime_param  # instant
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

        # collection exists?
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,),
        )
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

        # feature exists?
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

        properties = []

        if subTemporalValue:

            query = """
                SELECT
                    tp.property_name,
                    tp.property_type,
                    tp.form,
                    tp.description,
                    tv.interpolation,
                    array_agg(d.t ORDER BY d.idx) AS datetimes,
                    array_agg(v.val::float ORDER BY d.idx) AS values
                FROM temporal_properties tp
                LEFT JOIN temporal_values tv ON tp.id = tv.property_id
                CROSS JOIN LATERAL unnest(tv.datetimes) WITH ORDINALITY AS d(t, idx)
                CROSS JOIN LATERAL jsonb_array_elements_text(tv.values) WITH ORDINALITY AS v(val, idx2)
                WHERE tp.feature_id = %s
                  AND d.idx = v.idx2
                  AND d.t >= %s
                  AND d.t <= %s
                GROUP BY tp.property_name,
                         tp.property_type,
                         tp.form,
                         tp.description,
                         tv.interpolation
                ORDER BY tp.property_name
                LIMIT %s
            """

            cursor.execute(query, (feature_id, dt1, dt2, limit))
            rows = cursor.fetchall()

            temporal_properties_obj = {"datetimes": []}

            for row in rows:
                name = row[0]

                if not temporal_properties_obj["datetimes"]:
                    temporal_properties_obj["datetimes"] = [
                        dt.isoformat() if hasattr(dt, "isoformat") else dt
                        for dt in row[5]
                    ]

                temporal_properties_obj[name] = {
                    "type": row[1],
                    "form": row[2],
                    "values": row[6],
                    "interpolation": row[4] or "Linear",
                    "description": row[3],
                }

            properties = [temporal_properties_obj] if rows else []

        else:

            query = """
                SELECT DISTINCT
                    tp.property_name,
                    tp.property_type,
                    tp.form,
                    tp.description
                FROM temporal_properties tp
                LEFT JOIN temporal_values tv
                    ON tp.id = tv.property_id
                WHERE tp.feature_id = %s
            """

            params = [feature_id]

            if dt1 and dt2:
                query += """
                    AND EXISTS (
                        SELECT 1
                        FROM unnest(tv.datetimes) AS d(t)
                        WHERE d.t >= %s
                          AND d.t <= %s
                    )
                """
                params += [dt1, dt2]

            query += """
                ORDER BY tp.property_name
                LIMIT %s
            """

            params.append(limit)

            cursor.execute(query, params)

            rows = cursor.fetchall()

            for row in rows:
                properties.append({
                    "name": row[0],
                    "type": row[1],
                    "form": row[2],
                    "interpolation": "linear",
                    "description": row[3],
                })

        # response
        path = f"/collections/{collection_id}/items/{feature_id}/tproperties"

        response = build_properties_list_response(
            properties,
            "",
            path,
        )

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