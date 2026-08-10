from typing import List

from fastapi import APIRouter, Depends, status,Body, Query
from db.db import get_db
from resource.temporal_properties.Retrieve import get_tproperties
from resource.temporal_properties.Create import post_tproperties
from resource.temporal_property.Retrieve import get_temporal_property
from resource.temporal_property.Create import post_temporal_property
from resource.temporal_property.Delete import delete_temporal_property
from resource.temporal_prim_value.Delete import delete_temporal_primitive_value
# from sqlmodel.ext.asyncio.session import AsyncSession


# it 2 
from resource.temporal_properties.models import (
    TemporalPropertiesCreateRequest,
    TemporalPropertyValuesCreate,
    TemporalPropertiesResponse,
    TemporalPropertyDetailResponse,
)
# from src.auth.dependencies import AccessTokenBearer, RoleChecker
# from src.db.main import get_session
# GET
# POST
# /collections/{collection_id}/items/{mfeature_id}/tproperties

# GET
# POST
# DELETE
# /collections/{collection_id}/items/{mfeature_id}/tproperties/{property_name}

# DELETE
# /collections/{collection_id}/items/{mfeature_id}/tproperties/{property_name}/{value_id}


tproperties_router = APIRouter()


@tproperties_router.get("",response_model=TemporalPropertiesResponse)
async def get_tproperties_route(
    collection_id: str,
    mfeature_id: str,
    limit: int = Query(10, le=10000),
    datetime: str | None = None,
    subTemporalValue: bool = False,
    db=Depends(get_db),
):
    return await get_tproperties(
        collection_id=collection_id,
        feature_id=mfeature_id,
        limit=limit,
        datetime_param=datetime,
        subTemporalValue=subTemporalValue,
        db=db,
    )


@tproperties_router.post("", status_code=201)
async def post_tproperties_route(
    collection_id: str,
    mfeature_id: str,
    payload: TemporalPropertiesCreateRequest,
    db=Depends(get_db)
):
    return await post_tproperties(
        collection_id=collection_id,
        feature_id=mfeature_id,
        data=payload.model_dump(exclude_none=True),
        db=db,
    )


@tproperties_router.get("/{property_name}",response_model=TemporalPropertyDetailResponse)
async def get_temporal_property_route(
    collection_id: str,
    mfeature_id: str,
    property_name: str,
    datetime: str | None = Query(None),
    subTemporalValue: bool = Query(False),
    db=Depends(get_db),
):
    return await get_temporal_property(
        collection_id=collection_id,
        feature_id=mfeature_id,
        property_name=property_name,
        datetime_param=datetime,
        subTemporalValue=subTemporalValue,
        db=db,
    )


@tproperties_router.post("/{property_name}",status_code=201)
async def post_temporal_property_route(
    collection_id: str,
    mfeature_id: str,
    property_name: str,
    payload: TemporalPropertyValuesCreate,
    db=Depends(get_db),
):
    return await post_temporal_property(
        collection_id,
        mfeature_id,
        property_name,
        payload.model_dump(exclude_none=True),
        db,
    )

@tproperties_router.delete("/{property_name}", status_code=204)
async def delete_temporal_property_route(
    collection_id: str,
    mfeature_id: str,
    property_name: str,
    db=Depends(get_db)
):

    connection, cursor = db

    delete_temporal_property(
        collection_id,
        mfeature_id,
        property_name,
        connection,
        cursor
    )

    return None

@tproperties_router.delete("/{property_name}/{value_id}", status_code=204)
async def delete_temporal_property_value(
    collection_id: str,
    mfeature_id: str,
    property_name: str,
    value_id: str,
    db=Depends(get_db)
):

    connection, cursor = db

    delete_temporal_primitive_value(
        collection_id,
        mfeature_id,
        property_name,
        value_id,
        connection,
        cursor
    )

    return