from fastapi.responses import StreamingResponse
from resource.lakehouse.export import export_collection_to_parquet
from resource.lakehouse.iceberg import parquet_to_iceberg
from fastapi import APIRouter, Depends, status, Response
from db.mobilitydb import get_db
lakehouse_router = APIRouter()

@lakehouse_router.get("/export")
async def export_collection(
    collection_id: str,
    db=Depends(get_db),
):
    output = await export_collection_to_parquet(
        collection_id=collection_id,
        db=db,
    )

    return StreamingResponse(
        output,
        media_type="application/vnd.apache.parquet",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{collection_id}.parquet"'
            )
        },
    )


@lakehouse_router.post("/ingest")
async def ingest_collection(
    collection_id: str,
    db=Depends(get_db),
):
    # 1. Export the collection from MobilityDB
    output = await export_collection_to_parquet(
        collection_id=collection_id,
        db=db,
    )

    # 2. Send the generated Parquet into Iceberg
    table_name = parquet_to_iceberg(
        output.getvalue(),
        collection_id,
    )

    return {
        "status": "success",
        "collection_id": collection_id,
        "iceberg_table": table_name,
    }
