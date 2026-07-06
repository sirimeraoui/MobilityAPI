from fastapi import APIRouter, Request, Depends
from db import get_db
from resource.temporal_geom_seq.Retrieve import get_tgsequence
from resource.temporal_geom_seq.Create import post_tgsequence

tgeomseq_router = APIRouter()

@tgeomseq_router.get("")
async def get_tgsequence():
    pass

@tgeomseq_router.post("")
async def post_tgsequence():
    pass

@tgeomseq_router.get("/{tgeometry_id}")
async def get_tgsequence_item(tgeometry_id: str):
    pass

@tgeomseq_router.delete("/{tgeometry_id}")
async def delete_tgsequence_item(tgeometry_id: str):
    pass