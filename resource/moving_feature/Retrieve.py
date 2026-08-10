# REQ 19: /req/movingfeatures/mf-get
# REQ 21: /req/movingfeatures/mf-get-success
from resource.moving_feature.feature_helper import build_feature_from_row
import traceback
from fastapi import HTTPException


def get_movement_single_moving_feature(
    collection_id: str,
    feature_id: str,
    connection,
    cursor
):
    conn = connection

    try:
        # Check collection exists
        cursor.execute(
            """
            SELECT id
            FROM collections
            WHERE id = %s
            """,
            (collection_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        # Get feature with its temporal geometries
        cursor.execute(
            """
            SELECT
                mf.id,
                mf.type,
                mf.properties,
                mf.bbox::text,
                mf.time::text,
                mf.crs,
                mf.trs,
                json_agg(
                    json_build_object(
                        'id', tg.id,
                        'type', tg.geometry_type,
                        'trajectory', asMFJSON(tg.trajectory),
                        'interpolation', tg.interpolation,
                        'base', tg.base
                    )
                ) FILTER (WHERE tg.id IS NOT NULL) AS temporal_geometries
            FROM moving_features mf
            LEFT JOIN temporal_geometries tg
                ON mf.id = tg.feature_id
            WHERE mf.collection_id = %s
              AND mf.id = %s
            GROUP BY
                mf.id,
                mf.type,
                mf.properties,
                mf.bbox,
                mf.time,
                mf.crs,
                mf.trs
            """,
            (collection_id, feature_id),
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_id}' not found in collection '{collection_id}'"
            )

        feature = build_feature_from_row(
            row,
            collection_id,
            include_temporal=True,
            single=True,
        )

        return feature

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )