from fastapi import FastAPI
# from src.auth.routes import auth_router
from resource.collections.routes import collections_router
from resource.moving_features.routes import mfeatures_router
from resource.temporal_properties.routes import tproperties_router
from resource.temporal_geom_seq.routes import tgeomseq_router
# from .errors import register_all_errors
# from .middleware import register_middleware
import psycopg2 



version = "v1"

description = """
An open-source implementation of the [OGC API – Moving Features Standard](https://docs.ogc.org/is/22-003r3/22-003r3.html), built on top of [MobilityDB](https://github.com/MobilityDB/MobilityDB/).
    """

version_prefix =f"/api/{version}"

app = FastAPI(
    title="MobilityDB API",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Sirine AMERAOUI",
        "url": "https://github.com/",
        "email": "sirineameraoui@gmail.com",
    },
    # terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

# register_all_errors(app)

# register_middleware(app)


                   
app.include_router(
    collections_router,
    prefix=f"{version_prefix}/collections",
    tags=["Collections"],
)

app.include_router(
    mfeatures_router,
    prefix=f"{version_prefix}/collections/{{collection_id}}/items",
    tags=["Moving Features"],
)

app.include_router(
    tproperties_router,
    prefix=f"{version_prefix}/collections/{{collection_id}}/items/{{mfeature_id}}/tproperties",
    tags=["Temporal Properties"],
)

app.include_router(
    tgeomseq_router,
    prefix=f"{version_prefix}/collections/{{collection_id}}/items/{{mfeature_id}}/tgsequence",
    tags=["Temporal Geometries"],
)