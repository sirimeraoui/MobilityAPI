from typing import Any, Literal
from pydantic import BaseModel, ConfigDict
from resource.common.models import LinkResponse

class TemporalGeometryCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "MovingPoint"
    datetimes: list[str]
    coordinates: list[list[float]]
    interpolation: str = "Linear"
    base: dict[str, Any] | None = None
    orientations: list[dict[str, Any]] | None = None




# ------------------------------------Resp MOdels

class TemporalGeometryItemResponse(BaseModel):
    id: int
    type: str
    datetimes: list[str]
    coordinates: list[list[float]]
    interpolation: str | None = None
    base: Any | None = None

class TemporalGeometrySequenceResponse(BaseModel):
    type: Literal["TemporalGeometrySequence"]
    geometrySequence: list[TemporalGeometryItemResponse]
    links: list[LinkResponse]
    timeStamp: str
    numberMatched: int
    numberReturned: int




