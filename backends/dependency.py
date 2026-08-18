from config import Config

from db.mobilitydb import AsyncSessionLocal
from db.mobilityduck import create_mobilityduck_connection

from backends.mobilitydb.collections import (
    MobilityDBCollectionsBackend,
)

from backends.mobilityduck.collections import (
    MobilityDuckCollectionsBackend,
)


async def get_collections_backend():

    if Config.BACKEND == "mobilitydb":
        async with AsyncSessionLocal() as session:
            yield MobilityDBCollectionsBackend(session)
        return

    if Config.BACKEND == "mobilityduck":
        con = create_mobilityduck_connection()

        try:
            yield MobilityDuckCollectionsBackend(con)
        finally:
            con.close()

        return

    # future:
    # if Config.BACKEND == "mobilityspark":
    #     ...

    raise RuntimeError(
        f"Unsupported backend: {Config.BACKEND}"
    )