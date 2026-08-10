from typing import Any, Literal
from pydantic import (BaseModel,ConfigDict,model_validator)
from resource.common.models import LinkResponse

PropertyType = Literal["TBoolean","TText","TInteger","TReal","TImage",]

InterpolationType = Literal["Discrete","Step","Linear","Regression"]


class TemporalPropertyMetadataCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: PropertyType
    form: str | None = None
    description: str | None = None


class TemporalPropertyWithValuesCreate(BaseModel):
    # The property name itself is dynamic:
    # {"datetimes": [...], "speed": {...}}

    model_config = ConfigDict(extra="allow")

    datetimes: list[str]

    @model_validator(mode="before")
    @classmethod
    def validate_dynamic_property(cls, data):
        if not isinstance(data, dict):
            return data

        property_names = [
            key for key in data
            if key != "datetimes"
        ]

        if len(property_names) != 1:
            raise ValueError(
                "Exactly one temporal property must be provided"
            )

        property_data = data[property_names[0]]

        if not isinstance(property_data, dict):
            raise ValueError(
                "Temporal property definition must be an object"
            )

        if property_data.get("type") not in {
            "TBoolean",
            "TText",
            "TInteger",
            "TReal",
            "TImage",
        }:
            raise ValueError(
                "Invalid temporal property type"
            )

        values = property_data.get("values")

        if values is None:
            raise ValueError(
                "Missing required field: values"
            )

        if len(data.get("datetimes", [])) != len(values):
            raise ValueError(
                "datetimes and values must have the same length"
            )

        return data


TemporalPropertiesCreateRequest = (
    TemporalPropertyMetadataCreate
    | TemporalPropertyWithValuesCreate
)


class TemporalPropertyValuesCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    datetimes: list[str]
    values: list[Any]
    interpolation: InterpolationType = "Linear"

    @model_validator(mode="after")
    def validate_lengths(self):
        if len(self.datetimes) != len(self.values):
            raise ValueError(
                "datetimes and values must have the same length"
            )

        return self


# Res model+------------------------------------------------------------------------------------------------------

# Normal metadata representation
class TemporalPropertyResponse(BaseModel):
    name: str
    type: PropertyType
    form: str | None = None
    interpolation: InterpolationType | None = None
    description: str | None = None


class TemporalPropertyGroupedResponse(BaseModel):
    # Format 1 OGC representation:
    """{
        "datetimes": [...],
        "speed": {...},
        "temperature": {...}
    }"""
    
    # Property names are dynamic, therefore extra fields are allowed.

    model_config = ConfigDict(extra="allow")

    datetimes: list[str]


class TemporalPropertiesResponse(BaseModel):
    temporalProperties: list[
        TemporalPropertyResponse
        | TemporalPropertyGroupedResponse
    ]

    links: list[LinkResponse]
    timeStamp: str
    numberMatched: int
    numberReturned: int


class TemporalPropertyValueBlock(BaseModel):
    # Format 2 OGC representation:
    """{
        "datetimes": [...],
        "values": [...],
        "interpolation": "Linear"
    }"""

    datetimes: list[str]
    values: list[Any]
    interpolation: InterpolationType


class TemporalPropertyDetailResponse(BaseModel):
    temporalProperties: list[TemporalPropertyValueBlock]
    links: list[LinkResponse]