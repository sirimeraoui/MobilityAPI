from typing import List

from fastapi import APIRouter, Depends, status, Response,Request
from db.mobilitydb import get_db, get_async_db
from sqlmodel.ext.asyncio.session import AsyncSession

# ite 2 
from resource.moving_features.models import (
    MovingFeatureCreateRequest,
    MovingFeatureResponse,
    MovingFeatureCollectionResponse,
)
# from src.db.main import get_session
from resource.moving_features.Retrieve import get_collection_items
from resource.moving_features.Create import post_collection_items
from resource.moving_feature.Retrieve import get_movement_single_moving_feature
from resource.moving_feature.Delete import delete_single_moving_feature
from backends.dependency import get_moving_features_backend
# GET /collections/{collection_id}/items
# POST /collections/{collection_id}/items
# GET /collections/{collection_id}/items/{mfeature_id}
# DELETE /collections/{collection_id}/items/{mfeature_id}

mfeatures_router = APIRouter()

@mfeatures_router.get( "",response_model=MovingFeatureCollectionResponse)
async def retrieve_collection_items(
    collection_id: str,
    limit: int = 10,
    bbox: str | None = None,
    datetime: str | None = None,
    subTrajectory: bool = False,
    leaf: bool = False,
    backend=Depends(get_moving_features_backend)):
    
    return await get_collection_items(
        collection_id=collection_id,
        backend=backend,
        limit=limit,
        bbox=bbox,
        datetime_param=datetime,
        subTrajectory=subTrajectory,
        leaf=leaf,
    )

@mfeatures_router.post("", status_code=status.HTTP_201_CREATED)
async def create_collection_items(
    collection_id: str,
    payload: MovingFeatureCreateRequest,
    request:Request,
    backend=Depends(get_moving_features_backend)
):
    # connection, cursor = db

    return await post_collection_items(
        collection_id=collection_id,
        data=payload.model_dump(exclude_none=True),
        backend=backend,
        base_url=str(request.base_url),
    )

@mfeatures_router.get("/{mfeature_id}",response_model=MovingFeatureResponse)
async def get_moving_feature(
    collection_id: str,
    mfeature_id: str,
    backend=Depends(get_moving_features_backend),
):

    return await get_movement_single_moving_feature(
        collection_id=collection_id,
        feature_id=mfeature_id,
        backend=backend,
    )

@mfeatures_router.delete("/{mfeature_id}", status_code=204)
async def delete_moving_feature(
    collection_id: str,
    mfeature_id: str,
    backend=Depends(get_moving_features_backend),
):

    return await delete_single_moving_feature(
        collection_id=collection_id,
        feature_id=mfeature_id,
        backend=backend,
    )