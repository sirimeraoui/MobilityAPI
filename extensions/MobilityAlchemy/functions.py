from sqlalchemy.sql.functions import GenericFunction
from .types import TGeomPoint


# Gneeric functions was used to specify the return type here linking it to the UserDefined type Tgeompoint found in types.py.
#this avoids type related errors when the functions are used to fill the TemporalGeometry class object attributes:
# geometry and trajectory in for example /moving_features/Create.py
class tgeompointFromMFJSON(GenericFunction):
    type = TGeomPoint()
    inherit_cache = True


class setSRID(GenericFunction):
    type = TGeomPoint()
    inherit_cache = True

