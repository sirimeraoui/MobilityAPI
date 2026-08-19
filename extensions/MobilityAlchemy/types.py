from sqlalchemy.types import UserDefinedType


class TGeomPoint(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "tgeompoint"