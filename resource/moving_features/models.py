from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from resource.common.models import LinkResponse

class MovingFeatureCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["Feature"]
    id: str | int | None = None

    properties: dict[str, Any] = Field(default_factory=dict)

    temporalGeometry: dict[str, Any] | None = None
    temporalProperties: list[dict[str, Any]] | None = None

    time: Any | None = None
    crs: dict[str, Any] | None = None
    trs: dict[str, Any] | None = None


class MovingFeatureCollectionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["FeatureCollection"]
    features: list[MovingFeatureCreate]


MovingFeatureCreateRequest = Annotated[
    MovingFeatureCreate | MovingFeatureCollectionCreate,
    Field(discriminator="type"),
]



# ---------------------------------------response models

class TemporalGeometryResponse(BaseModel):
    id: int | str
    type: str
    datetimes: list[str] = Field(default_factory=list)
    coordinates: list[Any] = Field(default_factory=list)
    interpolation: str | None = None
    base: Any | None = None



class MovingFeatureBaseResponse(BaseModel):
    type: Literal["Feature"]
    id: str

    properties: dict[str, Any] = Field(default_factory=dict)
    bbox: list[float] = Field(default_factory=list)

    time: list[str] | str | None = None
    crs: dict[str, Any] | None = None
    trs: dict[str, Any] | None = None

    links: list[LinkResponse]


class MovingFeatureResponse(MovingFeatureBaseResponse):
    temporalGeometry: list[TemporalGeometryResponse] | None = None


class MovingFeatureListItemResponse(MovingFeatureBaseResponse):
    geometry: list[dict[str, Any]] = Field(default_factory=list)
    temporalGeometry: list[TemporalGeometryResponse] = Field(
        default_factory=list
    )


class MovingFeatureCollectionResponse(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[MovingFeatureListItemResponse]

    timeStamp: str
    numberMatched: int
    numberReturned: int

    links: list[LinkResponse]