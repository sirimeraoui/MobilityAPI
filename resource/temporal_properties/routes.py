from typing import List

from fastapi import APIRouter, Depends, status
from db import get_db
# from sqlmodel.ext.asyncio.session import AsyncSession

# from src.auth.dependencies import AccessTokenBearer, RoleChecker
# from src.books.service import BookService
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


@tproperties_router.get("")

@tproperties_router.post("")

@tproperties_router.get("/{property_name}")

@tproperties_router.post("/{property_name}")

@tproperties_router.delete("/{property_name}")


@tproperties_router.delete("/{property_name}/{value_id}")
async def delete_temporal_property_value():
    pass