from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    update_frequency: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    item_type: Mapped[str] = mapped_column(
        String,
        default="movingfeature",
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
    )