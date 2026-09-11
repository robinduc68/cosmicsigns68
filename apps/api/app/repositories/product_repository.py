"""Data access for products. The service layer never writes SQL itself."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> list[Product]:
        result = await self._session.execute(
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.sort_order, Product.price_amount)
        )
        return list(result.scalars().all())

    async def get_by_code(self, code: str) -> Product | None:
        result = await self._session.execute(select(Product).where(Product.code == code))
        return result.scalar_one_or_none()
