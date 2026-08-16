# resource/lakehouse/export.py

import json
import io

import pyarrow as pa
import pyarrow.parquet as pq

from fastapi import HTTPException


async def export_collection_to_parquet(
    collection_id: str,
    db,
):
    connection, cursor = db

    try:
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
                detail=f"Collection '{collection_id}' not found",
            )

        cursor.execute(
            """
            SELECT
                mf.id AS entity_id,

                asBinary(tg.trajectory) AS traj,

                Xmin(stbox(tg.trajectory)) AS xmin,
                Xmax(stbox(tg.trajectory)) AS xmax,
                Ymin(stbox(tg.trajectory)) AS ymin,
                Ymax(stbox(tg.trajectory)) AS ymax,

                Tmin(stbox(tg.trajectory)) AS tmin,
                Tmax(stbox(tg.trajectory)) AS tmax,

                SRID(tg.trajectory) AS srid

            FROM moving_features mf

            JOIN temporal_geometries tg
                ON mf.id = tg.feature_id
                AND mf.collection_id = tg.collection_id

            WHERE mf.collection_id = %s

            ORDER BY mf.id
            """,
            (collection_id,),
        )

        rows = cursor.fetchall()


        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No trajectories found in collection '{collection_id}'",
            )

# convett db rows into parquet columns
        entity_ids = []
        trajectories = []
        xmins = []
        xmaxs = []
        ymins = []
        ymaxs = []
        tmins = []
        tmaxs = []
        srids = []

        for row in rows:
            (
                entity_id,
                traj,
                xmin,
                xmax,
                ymin,
                ymax,
                tmin,
                tmax,
                srid,
            ) = row

            entity_ids.append(str(entity_id))

            # psycopg2 may already return BYTEA as bytes
            if traj is not None and not isinstance(traj, bytes):
                traj = bytes(traj)

            trajectories.append(traj)

            xmins.append(xmin)
            xmaxs.append(xmax)
            ymins.append(ymin)
            ymaxs.append(ymax)

            tmins.append(tmin)
            tmaxs.append(tmax)

            srids.append(srid)

# to arrow table
        table = pa.table(
            {
                "entity_id": pa.array(entity_ids),
                "traj": pa.array(trajectories, type=pa.binary()),

                "xmin": pa.array(xmins, type=pa.float64()),
                "xmax": pa.array(xmaxs, type=pa.float64()),
                "ymin": pa.array(ymins, type=pa.float64()),
                "ymax": pa.array(ymaxs, type=pa.float64()),

                "tmin": pa.array(tmins),
                "tmax": pa.array(tmaxs),

                "srid": pa.array(srids, type=pa.int32()),
            }
        )

# parquet metadata
        temporal_metadata = {
            "version": "1.0.0",
            "primary_temporal_column": "traj",
            "columns": {
                "traj": {
                    "encoding": "MEOS-WKB",
                    "encoding_version": "1.0",
                    "base_type": "tgeompoint",
                    "subtype": "Sequence",
                    "interpolation": "linear",
                    "srid": 4326,
                    "geodetic": False,
                    "has_z": False,
                }
            },
        }

# add temporeal parquet footer
        metadata = dict(table.schema.metadata or {})

        metadata[b"temporal"] = json.dumps(
            temporal_metadata
        ).encode("utf-8")

        table = table.replace_schema_metadata(metadata)


        output = io.BytesIO()

        pq.write_table(
            table,
            output,
            compression="snappy",
        )

        output.seek(0)

        return output

    except HTTPException:
        raise

    except Exception as e:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lakehouse export failed: {str(e)}",
        )