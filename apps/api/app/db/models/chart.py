from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, JSONColumn, TimestampMixin, UUIDPrimaryKeyMixin


class Chart(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A birth chart: the input the user gave plus the engine output.

    The birth input is stored column-by-column rather than as a blob so it can be
    validated, re-run against a newer engine version and deleted on request.
    """

    __tablename__ = "charts"
    __table_args__ = (Index("ix_charts_user_created", "user_id", "created_at"),)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    subject_name: Mapped[str] = mapped_column(String(120), nullable=False)
    relationship_label: Mapped[str | None] = mapped_column(String(60))
    gender: Mapped[str] = mapped_column(String(8), nullable=False)

    calendar_type: Mapped[str] = mapped_column(String(8), nullable=False)
    birth_day: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_month: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_year: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_minute: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_leap_month: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    birth_place: Mapped[str | None] = mapped_column(String(160))
    timezone_name: Mapped[str] = mapped_column(String(64), default="Asia/Ho_Chi_Minh")
    tz_offset: Mapped[float] = mapped_column(Float, default=7.0, nullable=False)
    note: Mapped[str | None] = mapped_column(String(500))

    engine_stage: Mapped[str] = mapped_column(String(16), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(32), nullable=False)
    chart_json: Mapped[dict[str, Any]] = mapped_column(JSONColumn, nullable=False)

    # Lets a retried "Lập lá số" submit return the chart that was already created
    # instead of producing a duplicate.
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
