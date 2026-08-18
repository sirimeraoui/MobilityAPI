from sqlalchemy.types import UserDefinedType
from pymeos import TGeomPoint 

class TGeomPoint(UserDefinedType):
    """
    SQLAlchemy representation of the MobilityDB tgeompoint type.

    Python values are represented using PyMEOS temporal geometric
    point objects:
      - TGeomPointInst
      - TGeomPointSeq
      - TGeomPointSeqSet
    """

    cache_ok = True

    def get_col_spec(self, **kw):
        return "tgeompoint"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None

            if not isinstance(value, TGeomPoint):
                raise TypeError(
                    f"Expected a PyMEOS TGeomPoint, got {type(value).__name__}"
                )

            return str(value)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None

            return TGeomPoint.read_from_cursor(value)

        return process