from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from db.base import Base
from extensions.MobilityAlchemy import TGeomPoint


class TemporalGeometry(Base):
    __tablename__ = "temporal_geometries"

    id: Mapped[int] = mapped_column(Integer,primary_key=True)

    feature_id: Mapped[str] = mapped_column(String)

    collection_id: Mapped[str] = mapped_column(String)

    geometry_type: Mapped[str | None] = mapped_column(String,nullable=True)

    # geometry = mapped_column(Geometry(),nullable=True)
    geometry = mapped_column(Geometry(geometry_type='POINT', srid=4326),nullable=True)

 


    trajectory = mapped_column(TGeomPoint(),nullable=True)

    interpolation: Mapped[str | None] = mapped_column(String,nullable=True)

    base = mapped_column(JSONB,nullable=True)

    orientations = mapped_column(JSONB,nullable=True)