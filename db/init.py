from config import Config

from db.mobilitydb import init_mobilitydb
from db.mobilityduck import init_mobilityduck


async def init_backend():
    if Config.BACKEND == "mobilitydb":
        await init_mobilitydb()
        return

    if Config.BACKEND == "mobilityduck":
        init_mobilityduck()
        return

    raise RuntimeError(
        f"Unsupported backend: {Config.BACKEND}"
    )