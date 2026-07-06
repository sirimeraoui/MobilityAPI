from typing import List

from fastapi import APIRouter, Depends, status,Body, Response
from db import get_db
# from sqlmodel.ext.asyncio.session import AsyncSession

# from src.auth.dependencies import AccessTokenBearer, RoleChecker

# from src.db.main import get_session
from resource.moving_features.Retrieve import get_collection_items
from resource.moving_features.Create import post_collection_items
from resource.moving_feature.Retrieve import get_movement_single_moving_feature
from resource.moving_feature.Delete import delete_single_moving_feature

# GET /collections/{collection_id}/items
# POST /collections/{collection_id}/items

# GET /collections/{collection_id}/items/{mfeature_id}
# DELETE /collections/{collection_id}/items/{mfeature_id}
mfeatures_router = APIRouter()


@mfeatures_router.get("")
async def retrieve_collection_items(
    collection_id: str,
    limit: int = 10,
    bbox: str | None = None,
    datetime: str | None = None,
    subTrajectory: bool = False,
    leaf: bool = False,
    db=Depends(get_db),
):
    connection, cursor = db

    return await get_collection_items(
        collection_id=collection_id,
        db=db,
        limit=limit,
        bbox=bbox,
        datetime_param=datetime,
        subTrajectory=subTrajectory,
        leaf=leaf,
    )


@mfeatures_router.post("", status_code=status.HTTP_201_CREATED)
async def create_collection_items(
    collection_id: str,
    data: dict = Body(...),
    db=Depends(get_db),
):
    connection, cursor = db

    return post_collection_items(
        collection_id=collection_id,
        data=data,
        connection=connection,
        cursor=cursor,
    )


@mfeatures_router.get("/{mfeature_id}")
async def get_moving_feature(
    collection_id: str,
    mfeature_id: str,
    db=Depends(get_db),
):
    connection, cursor = db

    return get_movement_single_moving_feature(
        collection_id=collection_id,
        feature_id=mfeature_id,
        connection=connection,
        cursor=cursor,
    )


@mfeatures_router.delete("/{mfeature_id}", status_code=204)
async def delete_moving_feature(
    collection_id: str,
    mfeature_id: str,
    db=Depends(get_db),
):
    connection, cursor = db

    return delete_single_moving_feature(
        collection_id=collection_id,
        feature_id=mfeature_id,
        connection=connection,
        cursor=cursor,
    )