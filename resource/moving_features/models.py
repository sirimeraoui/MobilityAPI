from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from resource.common.models import LinkResponse
from resource.temporal_geom_seq.models import (
    TemporalGeometryCreate,
    TemporalGeometryItemResponse
)

class MovingFeatureCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["Feature"]
    id: str | int | None = None

    properties: dict[str, Any] = Field(default_factory=dict)

    temporalGeometry: TemporalGeometryCreate | None = None
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

class MovingFeatureBaseResponse(BaseModel):
    type: Literal["Feature"]
    id: str

    properties: dict[str, Any] = Field(default_factory=dict)
    bbox: list[float] = Field(default_factory=list)

    time: list[str] | str | None = None
    crs: dict[str, Any] | None = None
    trs: dict[str, Any] | None = None

    links: list[LinkResponse]


# either it has one object, or we return the first object, tgsequence for all tg.
class MovingFeatureResponse(MovingFeatureBaseResponse):
    temporalGeometry: (
        TemporalGeometryItemResponse
        | list[TemporalGeometryItemResponse]
        | None
    ) = None
    geometry: (
        dict[str, Any]
        | list[dict[str, Any]]
        | None
    ) = None


class MovingFeatureListItemResponse(MovingFeatureBaseResponse):
    geometry: list[dict[str, Any]] = Field(default_factory=list)
    temporalGeometry: list[TemporalGeometryItemResponse] = Field(
        default_factory=list
    )


class MovingFeatureCollectionResponse(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[MovingFeatureListItemResponse]

    timeStamp: str
    numberMatched: int
    numberReturned: int

    links: list[LinkResponse]