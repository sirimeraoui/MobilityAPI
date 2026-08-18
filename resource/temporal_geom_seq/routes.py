from fastapi import APIRouter, Depends
from fastapi import HTTPException, Response
from resource.temporal_geom_seq.Retrieve import get_tgsequence
from resource.temporal_geom_seq.Create import post_tgsequence
from resource.temporal_prim_geom.Delete import delete_single_temporal_primitive_geo

from resource.temporal_geom_query.distance import get_distance
from resource.temporal_geom_query.velocity import get_velocity
from resource.temporal_geom_query.acceleration import get_acceleration
from fastapi import APIRouter, Depends, Response


# it2
from resource.temporal_geom_seq.models import (
    TemporalGeometryCreate,
    TemporalGeometrySequenceResponse,
)
from resource.temporal_geom_query.models import TemporalGeometryQueryResponse
from db.mobilitydb import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

tgeomseq_router = APIRouter()


@tgeomseq_router.get("",response_model=TemporalGeometrySequenceResponse,)
async def get_tgsequence_route(
    collection_id: str,
    mfeature_id: str,
    session: AsyncSession = Depends(get_async_db)
):

    return await get_tgsequence(
        collection_id,
        mfeature_id,
        session
    )


@tgeomseq_router.post("")
async def post_tgsequence_route(
    collection_id: str,
    mfeature_id: str,
    response: Response,
    payload: TemporalGeometryCreate,
    session : AsyncSession=Depends(get_async_db),
):

    return await post_tgsequence(
        collection_id,
        mfeature_id,
        response,
        session,
        data=payload.model_dump(),
    )

@tgeomseq_router.delete("/{tgeometry_id}", status_code=204)
async def delete_tgsequence_item(
    collection_id: str,
    mfeature_id: str,
    tgeometry_id: str,
    db=Depends(get_db)
):
    connection, cursor = db

    delete_single_temporal_primitive_geo(
        collection_id,
        mfeature_id,
        tgeometry_id,
        connection,
        cursor
    )


# ==========================================================
# TEMPORAL GEOMETRY QUERY
# ==========================================================

@tgeomseq_router.get(
    "/{tgeometry_id}/distance",
    response_model=TemporalGeometryQueryResponse,
)
async def get_tgsequence_distance(
    collection_id: str,
    mfeature_id: str,
    tgeometry_id: str,
    db=Depends(get_db)
):
    connection, cursor = db

    return await get_distance(
        collection_id,
        mfeature_id,
        tgeometry_id,
        connection,
        cursor
    )


@tgeomseq_router.get(
    "/{tgeometry_id}/velocity",
    response_model=TemporalGeometryQueryResponse,
)
async def get_tgsequence_velocity(
    collection_id: str,
    mfeature_id: str,
    tgeometry_id: str,
    db=Depends(get_db)
):
    connection, cursor = db

    return await get_velocity(
        collection_id,
        mfeature_id,
        tgeometry_id,
        connection,
        cursor
    )

@tgeomseq_router.get(
    "/{tgeometry_id}/acceleration",
    response_model=TemporalGeometryQueryResponse,
)
async def get_tgsequence_acceleration(
    collection_id: str,
    mfeature_id: str,
    tgeometry_id: str,
    db=Depends(get_db)
):
    connection, cursor = db
    return await get_acceleration(
        collection_id,
        mfeature_id,
        tgeometry_id,
        connection,
        cursor
    )