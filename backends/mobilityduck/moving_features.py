import uuid
import re
import json
from backends.base.moving_features import MovingFeaturesBackend

class MobilityDuckMovingFeaturesBackend(MovingFeaturesBackend):

    def __init__(self, connection):
        self.connection = connection


    async def begin(self):
        self.connection.execute("BEGIN TRANSACTION")
    async def commit(self):
        self.connection.commit()
    async def rollback(self):
        self.connection.rollback()

    async def collection_exists(
        self,
        collection_id: str,
    ):
        row = self.connection.execute("""SELECT 1 FROM collections
            WHERE id = ? LIMIT 1 """,
            [collection_id],
        ).fetchone()
        return row is not None

    async def create(self,collection_id: str,feature: dict):
        feat_id = str(feature.get("id") or uuid.uuid4())
        properties = feature.get("properties", {})
        temporal_geometry = feature.get("temporalGeometry")
        crs = feature.get("crs")
        trs = feature.get("trs")
        srid = 4326

        if crs and isinstance(crs, dict):
            props = crs.get("properties", "")

            if isinstance(props, dict):
                props = props.get("name", "")

            match = re.search(r"(\d+)", str(props))

            if match:
                srid = int(match.group(1))

        # Insert moving feature
        inserted = self.connection.execute(
            """INSERT INTO moving_features (
                id,
                collection_id,
                type,
                properties,
                crs,
                trs)
            VALUES ( ?, ?, ?,
                CAST(? AS JSON),
                CAST(? AS JSON),
                CAST(? AS JSON) )
            ON CONFLICT (id) DO NOTHING RETURNING id""",
            [feat_id, collection_id, "Feature",
                json.dumps(properties),
                json.dumps(crs) if crs is not None else None,
                json.dumps(trs) if trs is not None else None,
            ]).fetchone()

        if inserted is None: return None

        if temporal_geometry:
            tgeom_mfjson = json.dumps(temporal_geometry)

            geometry_type = temporal_geometry.get("type","MovingPoint")

            interpolation = temporal_geometry.get("interpolation","Linear")

            base = temporal_geometry.get("base")
            orientations = temporal_geometry.get("orientations")

            # insert temporal geometry
            self.connection.execute("""INSERT INTO temporal_geometries (
                    feature_id,
                    collection_id,
                    geometry_type,
                    geometry,
                    trajectory,
                    interpolation,
                    base,
                    orientations )
                VALUES (?, ?, ?,
                    trajectory(setSRID(tgeompointFromMFJSON(?),?)),
                    setSRID(tgeompointFromMFJSON(?),?),
                    ?,
                    CAST(? AS JSON),
                    CAST(? AS JSON)
                )""",[ feat_id, collection_id, geometry_type,
                    tgeom_mfjson,
                    srid,
                    tgeom_mfjson,
                    srid,
                    interpolation,
                    json.dumps(base) if base is not None else None,
                    json.dumps(orientations)
                    if orientations is not None else None,
                ])

            # manual trigger: update bbox and time in moving features after adding a new temporal geometry
            self.connection.execute("""UPDATE moving_features
                SET bbox = ( SELECT extent(trajectory)
                        FROM temporal_geometries
                        WHERE feature_id = ?
                        AND collection_id = ?),
                    time = ( SELECT extent(timeSpan(trajectory))
                        FROM temporal_geometries
                        WHERE feature_id = ?
                        AND collection_id = ?)
                WHERE id = ?
                AND collection_id = ?
                """,[
                    feat_id,
                    collection_id,
                    feat_id,
                    collection_id,
                    feat_id,
                    collection_id])

        return feat_id
    async def get_items(
        self,
        collection_id: str,
        limit: int,
        bbox_coords=None,
        dt1=None,
        dt2=None,
        subTrajectory: bool = False,
    ):
        query = """
            WITH limited_features AS (
                SELECT DISTINCT mf.id, mf.created_at FROM moving_features mf
                LEFT JOIN temporal_geometries tg ON mf.id = tg.feature_id
                WHERE mf.collection_id = ?
            """

        params = [collection_id]
        if bbox_coords is not None:
            x1, y1, x2, y2 = bbox_coords
            srid = self.connection.execute(
                    """
                    SELECT srid(trajectory)
                    FROM temporal_geometries
                    WHERE collection_id = ?
                    AND trajectory IS NOT NULL
                    LIMIT 1
                    """,
                    [collection_id]
                ).fetchone()[0]
            bbox_stbox = f"SRID={srid};STBOX X(({x1},{y1}),({x2},{y2}))"

            query += """
                AND tg.trajectory && CAST(? AS stbox)
            """
            params.append(bbox_stbox)

        # defaults: full geometry + full trajectory
        geometry_expr = "ST_AsGeoJSON(tg.geometry)"
        trajectory_expr = "asMFJSON(tg.trajectory)"

        if dt1 and dt2:
            query += """AND tg.trajectory && CAST(? AS tstzspan)"""
            params.append(f"[{dt1}, {dt2}]")

        elif dt1:
            query += """AND tg.trajectory && CAST(? AS tstzspan)"""
            params.append(f"[{dt1}, {dt1}]")

        # special case: clipped trajectory
        if subTrajectory and dt1 and dt2:
            geometry_expr = """ST_AsGeoJSON(trajectory(atTime(tg.trajectory,CAST(? AS tstzspan))))"""

            trajectory_expr = """asMFJSON(atTime(tg.trajectory,CAST(? AS tstzspan)))"""
            

        query += f"""
            ORDER BY mf.created_at
            LIMIT ?)
        SELECT mf.id, mf.type, {geometry_expr}, mf.properties, mf.bbox::text, mf.time::text,
            mf.crs,
            mf.trs,
            tg.id,
            tg.geometry_type,
            {trajectory_expr},
            tg.interpolation,
            tg.base
        FROM limited_features lf
        JOIN moving_features mf ON mf.id = lf.id 
        LEFT JOIN temporal_geometries tg ON mf.id = tg.feature_id
        ORDER BY mf.created_at
        """
        params.append(limit)
        if subTrajectory and dt1 and dt2:
            params.append(f"[{dt1}, {dt2}]")
            params.append(f"[{dt1}, {dt2}]")
        result = self.connection.execute(query,params)
        rows = result.fetchall()
        normalized_rows = []
        for row in rows:
            row = list(row)
            # properties
            if isinstance(row[3], bytes):
                row[3] = json.loads(row[3].decode("utf-8"))
            elif isinstance(row[3], str):
                row[3] = json.loads(row[3])
            # crs
            if isinstance(row[6], bytes):
                row[6] = json.loads(row[6].decode("utf-8"))
            elif isinstance(row[6], str):
                row[6] = json.loads(row[6])
            # trs
            if isinstance(row[7], bytes):
                row[7] = json.loads(row[7].decode("utf-8"))
            elif isinstance(row[7], str):
                row[7] = json.loads(row[7])
            normalized_rows.append(tuple(row))

        return normalized_rows

# by feature id operations
    async def get_feature(
        self,
        collection_id: str,
        mfeature_id: str,
    ):
         # Get feature with its temporal geometries
        feature = self.connection.execute(
        """SELECT mf.id, mf.type, mf.properties, mf.bbox::text,
                mf.time::text, mf.crs, mf.trs,
                to_json(
                list(
                    json_object(
                        'id', tg.id,
                        'type', tg.geometry_type,
                        'trajectory', asMFJSON(tg.trajectory),
                        'interpolation', tg.interpolation,
                        'base', tg.base)
                    ) FILTER (WHERE tg.id IS NOT NULL)
                ) AS temporal_geometries,
                to_json(
                    list(ST_AsGeoJSON(trajectory(tg.trajectory))::json)
                FILTER (WHERE tg.id IS NOT NULL)) AS geometries
            FROM moving_features mf
            LEFT JOIN temporal_geometries tg
                ON mf.id = tg.feature_id
            WHERE mf.collection_id = ?
            AND mf.id = ?
            GROUP BY mf.id, mf.type, mf.properties, mf.bbox, mf.time,
                mf.crs,
                mf.trs
            """,[collection_id, mfeature_id])
        # return feature.fetchone()
        row = feature.fetchone()
        if row is None: return None
        row = list(row)
        def parse_json(value):
            if value is None: return None
            if isinstance(value, bytes): return json.loads(value.decode("utf-8"))
            if isinstance(value, str): return json.loads(value)
            return value

        row[2] = parse_json(row[2])  # properties
        row[5] = parse_json(row[5])  # crs
        row[6] = parse_json(row[6])  # trs
        row[7] = parse_json(row[7])  # temporalgeoms
        row[8] = parse_json(row[8])  # geometries
        return tuple(row)

# duckdb does't support cascade delete. And still throws foreign-key violation errors because the refences remain in the index. 
# current solution: remove references from db/mobilityduckdb.py initfunction, rely on the backend and wait for a new duckdb version :(
    async def delete(self,collection_id: str,mfeature_id: str):
        self.connection.execute("BEGIN TRANSACTION")
        # temporal_values depend on temporal_properties
        self.connection.execute("""DELETE FROM temporal_values
            WHERE property_id IN ( SELECT id FROM temporal_properties
                                    WHERE feature_id = ?)""",
            [mfeature_id])

        self.connection.execute("""DELETE FROM temporal_properties
            WHERE feature_id = ?""",
            [mfeature_id])

        self.connection.execute("""DELETE FROM temporal_geometries
            WHERE feature_id = ?
            AND collection_id = ?""",
            [mfeature_id, collection_id],
        )

        deleted = self.connection.execute(
            """DELETE FROM moving_features WHERE id = ?
            AND collection_id = ? RETURNING id""",
            [mfeature_id, collection_id]).fetchone()

        return deleted[0] if deleted else None

