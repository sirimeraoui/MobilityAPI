# REQ7: /req/mf-collection/collection-put
# RE10: /req/mf-collection/collection-put-success


async def put_collection(
    collection_id: str,
    data_dict: dict,
    backend,
):
    updated = await backend.replace(
        collection_id,
        data_dict,
    )

    if not updated:
        raise ValueError(
            f"Collection '{collection_id}' not found"
        )

    return True