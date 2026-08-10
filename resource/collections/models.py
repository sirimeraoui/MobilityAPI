# resource/collections/models.py

from typing import Literal,Any

from pydantic import BaseModel, ConfigDict


class CollectionCreate(BaseModel):
    # for safety, no additional input is allowed, if the OGC MF changes
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str | None = None
    itemType: Literal["movingfeature"] = "movingfeature"
    updateFrequency: int | None = None


class CollectionReplace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    itemType: Literal["movingfeature"] | None = None


    # ----------------------------------responses

class LinkResponse(BaseModel):
    href: str
    rel: str
    type: str | None = None

class SpatialExtentResponse(BaseModel):
    bbox: list[float]
    crs: Any | None = None


class TemporalExtentResponse(BaseModel):
    interval: list[str]
    trs: Any | None = None


class ExtentResponse(BaseModel):
    spatial: SpatialExtentResponse
    temporal: TemporalExtentResponse


# get one collection
class CollectionResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    itemType: Literal["movingfeature"]
    updateFrequency: int | None = None
    extent: ExtentResponse | None = None
    links: list[LinkResponse]

# get list of collections
class CollectionsResponse(BaseModel):
    collections: list[CollectionResponse]
    links: list[LinkResponse]