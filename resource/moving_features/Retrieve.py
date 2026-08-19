# REQ 14: /req/movingfeatures/features-get
# REQ16: /req/movingfeatures/features-get-success
# REQ50-52: Common params (limit, bbox, datetime) 
# REQ 12-13: subTrajectory param(ogc)
# REQ23-24: leaf param
import json
from datetime import datetime
from resource.moving_feature.feature_helper import build_feature_from_row, build_feature_collection_response
import traceback

from fastapi import HTTPException
from fastapi import HTTPException, Query
from datetime import datetime
import json



async def get_collection_items(
    collection_id: str,
    backend,
    limit: int = Query(10, le=10000),
    bbox: str | None = None,
    datetime_param: str | None = Query(None, alias="datetime"),
    subTrajectory: bool = False,
    leaf: bool = False
):
    # connection, cursor = db
    try:

      #quey params validation
        if subTrajectory and leaf:
            raise HTTPException(
                status_code=400,
                detail="subTrajectory cannot be used with leaf",
            )

        x1 = y1 = x2 = y2 = None
        bbox_coords = None
        if bbox:
            try:
                bbox_coords = [float(c) for c in bbox.split(",")]

                if len(bbox_coords) != 4:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid bbox format",
                    )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid bbox coordinates",
                )

        dt1 = dt2 = None

        if datetime_param:

            if "/" in datetime_param:

                dt1, dt2 = datetime_param.split("/")

                if subTrajectory and (not dt1 or not dt2):
                    raise HTTPException(
                        status_code=400,
                        detail="subTrajectory requires a bounded datetime interval",
                    )

            else:

                dt1 = datetime_param

                if subTrajectory:
                    raise HTTPException(
                        status_code=400,
                        detail="subTrajectory requires a bounded interval",
                    )

        if subTrajectory and not (dt1 and dt2):
            raise HTTPException(
                status_code=400,
                detail="subTrajectory requires a datetime interval",
            )


        if not await backend.collection_exists(collection_id):
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' not found",
            )

   
        # get limit first
   
        rows = await backend.get_items(
            collection_id=collection_id,
            limit=limit,
            bbox_coords=bbox_coords,
            dt1=dt1,
            dt2=dt2,
            subTrajectory=subTrajectory
        )

        if not rows:
            return {
                "type": "FeatureCollection",
                "features": [],
                "timeStamp": datetime.utcnow().isoformat() + "Z",
                "numberMatched": 0,
                "numberReturned": 0,
                "links": [],
            }

        features_dict = {}

        for row in rows:
            feature_id = row[0]

            if feature_id not in features_dict:
                feature_row = (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                )

                feature = build_feature_from_row(
                    feature_row,
                    collection_id,
                    include_temporal=False,
                )

                feature["geometry"] = []
                feature["temporalGeometry"] = []

                features_dict[feature_id] = feature

            if row[8]:
                geometry = row[2]
                mf_json = json.loads(row[10])

                if leaf and "datetimes" in mf_json:
                    mf_json["coordinates"] = [
                        mf_json["coordinates"][-1]
                    ]
                    mf_json["datetimes"] = [
                        mf_json["datetimes"][-1]
                    ]
                    mf_json["interpolation"] = "Discrete"

                temporal_geom = {
                    "id": row[8],
                    "type": row[9] or "MovingPoint",
                    "datetimes": mf_json.get("datetimes", []),
                    "coordinates": mf_json.get("coordinates", []),
                    "base": row[12],
                    "interpolation": (
                        mf_json["interpolation"]
                        if leaf and "interpolation" in mf_json
                        else row[11] or "Linear"
                    ),
                }

                features_dict[feature_id]["temporalGeometry"].append(
                    temporal_geom
                )

                if geometry:
                    features_dict[feature_id]["geometry"].append(
                        json.loads(geometry)
                    )

        total_count = len(features_dict)

        response = build_feature_collection_response(
            features=list(features_dict.values()),
            total_count=total_count,
            limit=limit,
            base_url="",
            path=f"/collections/{collection_id}/items",
            bbox=bbox,
            datetime_param=datetime_param,
        )

        return response

    except HTTPException:
        raise

    except Exception as e:
        await backend.rollback()
        raise HTTPException(
            status_code=500,
            detail={
        "error": str(e),
        "trace": traceback.format_exc()
    }
        )