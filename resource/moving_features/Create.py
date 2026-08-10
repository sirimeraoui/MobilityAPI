# REQ15: /req/movingfeatures/features-post
# REQ 17: /req/movingfeatures/features-post-success
import uuid
import json

from psycopg2 import sql
import traceback

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def post_collection_items(collection_id: str, data: dict, connection,cursor):

    conn = connection
    try:

        # Check collection exists
        cursor.execute(
            "SELECT id FROM collections WHERE id = %s",
            (collection_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found"
            )

        created_feature_ids = []

        if data["type"] == "FeatureCollection":

            # features = data.get("features")

            for feature in data["features"]:
                feature_id = insert_feature(
                    feature,
                    collection_id,
                    conn,
                    cursor
                )

                if feature_id:
                    created_feature_ids.append(feature_id)

        else:

            feature_id = insert_feature(
                data,
                collection_id,
                conn,
                cursor
            )

            if feature_id:
                created_feature_ids.append(feature_id)

        conn.commit()

        return JSONResponse(
            status_code=201,
            content={
                "message": f"Created {len(created_feature_ids)} features",
                "ids": created_feature_ids
            },
            headers={
                "Location":
                f"/collections/{collection_id}/items/{created_feature_ids[0]}"
                if created_feature_ids else ""
            }
        )

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        msg = str(e)

        if "duplicate key" in msg.lower():
            raise HTTPException(status_code=409, detail=msg)

        raise HTTPException(status_code=500, detail=msg)

#add single moving feature to moving_features table
def insert_feature(feature, collection_id, connection, cursor):

    # generate or use given feature ID
    feat_id = feature.get("id")
    if feat_id is None:
        feat_id = str(uuid.uuid4())
    else:
        feat_id = str(feat_id)
    bbox_calculated = None
    time_range_calculated = None


    # *convert temporalGeometry to TGeomPoint
    temporal_geometry = feature.get("temporalGeometry")
    tgeom_mfjson=None
    if temporal_geometry:
        if isinstance(temporal_geometry, dict): 
            tgeom_mfjson = json.dumps(temporal_geometry)
            
        # elif isinstance(temporal_geometry, str):
        #     print("eeee",flush=True)
        #     tgeom_mfjson = temporal_geometry

        # time range
        # time_range_calculated = [stbox.tmin().isoformat(), stbox.tmax().isoformat()]
        
    properties = feature.get("properties", {})
    #mf life span time range:
    time_range = feature.get("time")
    crs = feature.get("crs")
    trs = feature.get("trs")

    srid = 4326 #world,
    if crs and isinstance(crs, dict):
        props = crs.get("properties", "")

        # CRS can be either:
        # - "urn:ogc:def:crs:EPSG::25832"
        # - {"name": "EPSG::25832"}
        if isinstance(props, dict):
            props = props.get("name", "")

        import re
        match = re.search(r'(\d+)', str(props))

        if match:
            srid = int(match.group(1))
    # INSERT INTO moving_features :temporal_geometries:Insert feature into moving_features table


    columns = ["id", "collection_id", "type", "properties"]
    values = [feat_id, collection_id, "Feature", json.dumps(properties)]

    if crs is not None:
        columns.append("crs")
        values.append(json.dumps(crs))

    if trs is not None:
        columns.append("trs")
        values.append(json.dumps(trs))

    query = sql.SQL("""
        INSERT INTO moving_features ({fields})
        VALUES ({placeholders})
        ON CONFLICT (id) DO NOTHING
        RETURNING id
    """).format(
        fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
        placeholders=sql.SQL(", ").join(sql.Placeholder() * len(values))
    )
    # log_sql(cursor, query, values)
    cursor.execute(query, values)
    inserted = cursor.fetchone()

    # INSERT INTO temporal_geometries: If the create feature has a temporal_geom, then add to temporal_geometries table    
    #RE CHECK OGC (must the uiser always provide the temporal geom unsure 40 percent)
    
    if inserted and tgeom_mfjson:
        base = temporal_geometry.get("base",None)
        geometry_type = "MovingPoint"  # Default 
        if temporal_geometry and isinstance(temporal_geometry, dict):
            geometry_type = temporal_geometry.get("type", "MovingPoint") #get geom_type of not default MovingPoint
            interpolation = temporal_geometry.get("interpolation", "Linear")
           
            orientations = temporal_geometry.get("orientations",None)
        else:
            interpolation = "Linear"
        columns = ["feature_id","collection_id","geometry_type","geometry",
            "trajectory",
            "interpolation"
        ]
        values = [feat_id,collection_id,geometry_type,tgeom_mfjson,srid,tgeom_mfjson,
            srid,
            interpolation
        ]
        placeholders = [
            "%s", "%s", "%s",
            "trajectory(SETSRID(tgeompointFromMFJSON(%s), %s))",
            "SETSRID(tgeompointFromMFJSON(%s), %s)",
            "%s"
        ]
        if base is not None:
            columns.append("base")
            placeholders.append("%s")
            values.append(base)

        if orientations is not None:
            columns.append("orientations")
            placeholders.append("%s")
            values.append(orientations)


        query = f"""
                INSERT INTO temporal_geometries 
                ({", ".join(columns)})
                VALUES (
                    {", ".join(placeholders)}
                )
                RETURNING ID
            """
        
        # log_sql(cursor, query, values)
        cursor.execute(query, values)
        inserted = cursor.fetchone()
    if inserted:
        # print(f"Inserted feature {feat_id}")
        return feat_id
    else:
        return None