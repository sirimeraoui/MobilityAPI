from typing import Literal
from pydantic import BaseModel, Field


class TemporalQueryValuesResponse(BaseModel):
    datetimes: list[str] = Field(default_factory=list)
    values: list[float] = Field(default_factory=list)

# common 
class LinkResponse(BaseModel):
    href: str
    rel: str
    type: str


class TemporalGeometryQueryResponse(BaseModel):
    name: Literal["distance", "velocity", "acceleration"]
    type: Literal["TReal"]
    form: str
    description: str
    values: TemporalQueryValuesResponse
    links: list[LinkResponse]