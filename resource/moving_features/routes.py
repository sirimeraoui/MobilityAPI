from typing import List

from fastapi import APIRouter, Depends, status
from db import get_db
# from sqlmodel.ext.asyncio.session import AsyncSession

# from src.auth.dependencies import AccessTokenBearer, RoleChecker
# from src.books.service import BookService
# from src.db.main import get_session



# GET /collections/{collection_id}/items
# POST /collections/{collection_id}/items

# GET /collections/{collection_id}/items/{mfeature_id}
# DELETE /collections/{collection_id}/items/{mfeature_id}
mfeatures_router = APIRouter()


@mfeatures_router.get("")
async def get_collection_items():
    pass

@mfeatures_router.post("")
async def create_collection_items():
    pass

@mfeatures_router.get("/{mfeature_id}")
async def get_moving_feature():
    pass

@mfeatures_router.delete("/{mfeature_id}")
async def delete_moving_feature():
    pass