from enum import Enum
from resource.temporal_geom_query.models import (TemporalGeometryQueryResponse,TemporalQueryValuesResponse,LinkResponse)

#req 33 , response obj for temporal geometries distance, velocity and acceleration queries
def build_query_response(values, unit, query_type, base_url, path):
    description = QueryDescription[query_type].value

    return TemporalGeometryQueryResponse(
        name=query_type,
        type="TReal",
        form=unit,
        description=description,
        values=TemporalQueryValuesResponse(
            datetimes=values["datetimes"],
            values=values["values"],
        ),
        links=[
            LinkResponse(
                href=f"{base_url}{path}",
                rel="self",
                type="application/json",
            )
        ],
    )

class QueryDescription(Enum):
    distance="a graph of the time to distance function as a form of the TemporalProperty."
    velocity = "a graph of the time to velocity function as a form of the TemporalProperty."
    acceleration = "a graph of the time to acceleration function as a form of the TemporalProperty."
