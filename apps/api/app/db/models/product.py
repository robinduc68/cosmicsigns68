from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, JSONColumn, TimestampMixin, UUIDPrimaryKeyMixin


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A thing a user can buy, and what buying it unlocks.

    Prices live here rather than in the frontend or in code so an operator can
    change them without a deploy — see business.md, nguyên tắc bất biến #4.
    Rows are seeded by migration with the launch prices; after that the database
    is the only authority.
    """

    __tablename__ = "products"

    # Stable business identifier (`CAREER_READING`), used by checkout and by the
    # entitlement table. The UUID id is for row identity only.
    code: Mapped[str] = mapped_column(String(48), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Đồng has no minor unit in practice, so this is a whole-đồng integer.
    # Never a float: money must not round.
    price_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="VND", nullable=False)

    # Entitlement codes granted on purchase. `FULL_LIFETIME_READING` grants more
    # than its own code, which is why this is a list and not derived from `code`.
    entitlements: Mapped[list[str]] = mapped_column(JSONColumn, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
