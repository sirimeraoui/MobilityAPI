
from db.schemas.collection import Collection
from backends.base.moving_features import MovingFeaturesBackend
import uuid
import json
import re

from sqlalchemy import insert, func, text

from db.schemas.collection import Collection
from db.schemas.temporal_geometry import TemporalGeometry
from backends.base.moving_features import MovingFeaturesBackend

from extensions.MobilityAlchemy import (tgeompointFromMFJSON,setSRID)
class MobilityDBMovingFeaturesBackend(MovingFeaturesBackend):

    def __init__(self, session):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
    async def collection_exists(self, collection_id: str):
        collection = await self.session.get(
            Collection,
            collection_id,
        )
        return collection is not None


    async def create(self,collection_id: str,feature: dict):
 
        feat_id = str(feature.get("id") or uuid.uuid4())
        
        properties = feature.get("properties", {})
        temporal_geometry = feature.get("temporalGeometry")
    
        crs = feature.get("crs")
        trs = feature.get("trs")
        
        # srid
        srid = 4326
    
        if crs and isinstance(crs, dict):
            props = crs.get("properties", "")
    
            if isinstance(props, dict):
                props = props.get("name", "")
    
            match = re.search(
                r"(\d+)",
                str(props),
            )
    
            if match:
                srid = int(match.group(1))
    
    
    # insert feauture
        result = await self.session.execute(
            text("""
                INSERT INTO moving_features (id,collection_id,type,properties,crs,trs)
                VALUES (:id,:collection_id,:type,CAST(:properties AS jsonb),
                    CAST(:crs AS jsonb),
                    CAST(:trs AS jsonb)
                )
                ON CONFLICT (id) DO NOTHING
                RETURNING id
            """),
            {
                "id": feat_id,
                "collection_id": collection_id,
                "type": "Feature",
                "properties": json.dumps(properties),
                "crs": (json.dumps(crs) if crs is not None else None),
                "trs": (json.dumps(trs) if trs is not None else None),
            },
        )
        # result.scalar_one_or_none()
    # insert the temporal_geometry seuqence that was sent with the moving feautures it there is one
        if temporal_geometry:
            tgeom_mfjson = json.dumps(temporal_geometry)
    # LineString types can be added as well(orientations)
            geometry_type = temporal_geometry.get("type","MovingPoint")
            interpolation = temporal_geometry.get("interpolation","Linear")
            base = temporal_geometry.get("base")
            orientations = temporal_geometry.get("orientations")
            # using SQLALchemy defined functions and type
            trajectory_expr = setSRID(tgeompointFromMFJSON(tgeom_mfjson),srid)
    
            stmt = (
                insert(TemporalGeometry)
                .values(
                    feature_id=feat_id,
                    collection_id=collection_id,
                    geometry_type=geometry_type,
                    geometry=func.trajectory(trajectory_expr),
                    trajectory=trajectory_expr,    # trip
                    interpolation=interpolation,
                    base=base,
                    orientations=orientations,
                )
                .returning(
                    TemporalGeometry.id
                )
            )
    
            result = await self.session.execute(stmt)
    
            temporal_geometry_id = result.scalar_one()
    
            # print("Created temporal geometry:",temporal_geometry_id,"for feature",repr(inserted_feature))
    
        return feat_id
    async def get_items(self,collection_id: str,limit: int,bbox_coords=None,dt1=None,
        dt2=None,
        subTrajectory: bool = False,
    ):
        query = """
        WITH limited_features AS (
            SELECT DISTINCT mf.id, mf.created_at
            FROM moving_features mf
            LEFT JOIN temporal_geometries tg
                ON mf.id = tg.feature_id
            WHERE mf.collection_id = :collection_id
        """

        params = {
            "collection_id": collection_id,
            "limit": limit,
        }

        if bbox_coords is not None:
            x1, y1, x2, y2 = bbox_coords

            bbox_stbox = f"STBOX X(({x1},{y1}),({x2},{y2}))"

            query += """
                AND tg.trajectory &&
                setsrid(CAST(:bbox_stbox AS stbox),srid(tg.trajectory))
            """

            params["bbox_stbox"] = bbox_stbox

        # defaults: full geometry + full trajectory
        geometry_expr = "ST_AsGeoJSON(tg.geometry)"
        trajectory_expr = "asMFJSON(tg.trajectory)"

        if dt1 and dt2:
            query += """
                AND tg.trajectory && CAST(:period AS tstzspan)
            """
            params["period"] = f"[{dt1}, {dt2}]"

        elif dt1:
            query += """
                AND tg.trajectory && CAST(:period AS tstzspan)
            """
            params["period"] = f"[{dt1}, {dt1}]"

        # special case: clipped trajectory
        if subTrajectory and dt1 and dt2:
            geometry_expr = "ST_AsGeoJSON(trajectory(atTime(tg.trajectory,CAST(:period AS tstzspan))))"

            trajectory_expr = """asMFJSON(atTime(tg.trajectory,CAST(:period AS tstzspan)))"""

        query += f"""
            ORDER BY mf.created_at
            LIMIT :limit)
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

        result = await self.session.execute(text(query),params)

        return result.fetchall()
# by feature id operations:

    async def get(
        self,
        collection_id: str,
        mfeature_id: str,
    ):
        pass

    async def delete(
        self,
        collection_id: str,
        mfeature_id: str,
    ):
        pass
