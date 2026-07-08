from fastapi import APIRouter, Depends, Request, HTTPException
from db.db import get_db

from resource.collections.Retrieve import get_collections as get_collections_service
from resource.collections.Create import post_collections as post_collections_service
from resource.collection.Retrieve import get_collection_id
from resource.collection.Replace import put_collection
from resource.collection.Delete import delete_collection


collections_router = APIRouter()


@collections_router.get("")
def get_collections_route(request: Request, db=Depends(get_db)):
    conn, cursor = db
    base_url = str(request.base_url).rstrip("/")
    return get_collections_service(conn, cursor, base_url)


@collections_router.post("",status_code=201)
async def post_collections_route(request: Request, db=Depends(get_db)):
    conn, cursor = db

    try:
        data_dict = await request.json()

        collection_id, collection_data = post_collections_service(
            conn,
            cursor,
            data_dict,
            base_url=str(request.base_url).rstrip("/")
        )

        return {
            "message": "created",
            "collection": collection_data,
            "location": f"{request.base_url}collections/{collection_id}"
        }

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collections_router.get("/{collection_id}")
def get_collection_route(collection_id: str, request: Request, db=Depends(get_db)):
    conn, cursor = db

    try:
        base_url = str(request.base_url).rstrip("/")

        return get_collection_id(conn, cursor, collection_id, base_url)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collections_router.put("/{collection_id}", status_code=204)
async def put_collection_route(collection_id: str, request: Request, db=Depends(get_db)):
    conn, cursor = db

    try:
        data_dict = await request.json()

        put_collection(
            collection_id,
            data_dict,
            conn,
            cursor
        )

        return None

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collections_router.delete("/{collection_id}", status_code=204)
def delete_collection_route(collection_id: str, db=Depends(get_db)):
    conn, cursor = db

    try:
        delete_collection(collection_id, conn, cursor)
        return None

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))