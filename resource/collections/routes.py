from fastapi import APIRouter, Depends, Request, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from resource.collections.Retrieve import get_collections as get_collections_service
from resource.collections.Create import post_collections as post_collections_service
from resource.collection.Retrieve import get_collection_id
from resource.collection.Replace import put_collection
from resource.collection.Delete import delete_collection
from backends.dependency import get_collections_backend
# iteration 2
from resource.collections.models import (
    CollectionCreate,
    CollectionReplace,
    CollectionResponse,
    CollectionsResponse,
)

collections_router = APIRouter()


@collections_router.post("", status_code=201)
async def post_collections_route(
    payload: CollectionCreate,
    request: Request,
    backend=Depends(get_collections_backend)
):

    try:
        collection_id, collection_data = await post_collections_service(
            backend,
            payload.model_dump(),
            base_url=str(request.base_url).rstrip("/")
        )

        return {
            "message": "created",
            "collection": collection_data,
            "location": f"{request.base_url}collections/{collection_id}"
        }

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@collections_router.get("",response_model=CollectionsResponse)
async def get_collections_route(request: Request,backend=Depends(get_collections_backend)):
    base_url = str(request.base_url).rstrip("/")
    return await get_collections_service(backend,base_url)



@collections_router.get("/{collection_id}",response_model=CollectionResponse,)
async def get_collection_route(collection_id: str,
    request: Request,
    backend=Depends(get_collections_backend)
):

    try:
        base_url = str(request.base_url).rstrip("/")
        return await get_collection_id(backend,collection_id,base_url)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=500,
              # detail="Internal server error",
            detail=str(e))
        
@collections_router.put("/{collection_id}", status_code=204)
async def put_collection_route(
    collection_id: str,
    payload: CollectionReplace,
    backend=Depends(get_collections_backend)
):
    try:
        data_dict = payload.model_dump(exclude_unset=True)

        await put_collection(
            collection_id,
            data_dict,
            backend
        )

        return None

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@collections_router.delete("/{collection_id}", status_code=204)
async def delete_collection_route(collection_id: str,  backend=Depends(get_collections_backend)):

    try:
        await delete_collection(collection_id, backend)
        return None

    except HTTPException as e:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))