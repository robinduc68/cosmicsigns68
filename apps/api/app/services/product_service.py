"""Product use-cases.

Deliberately thin: the catalogue is operator-owned data, so the job here is to
read it out, not to decide what it should contain.
"""

from __future__ import annotations

from app.core.errors import NotFoundError
from app.db.models.product import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def list_active(self) -> list[Product]:
        return await self._repository.list_active()

    async def get_by_code(self, code: str) -> Product:
        product = await self._repository.get_by_code(code)
        # An inactive product is still readable by code: an order placed while it
        # was on sale must stay explainable after it is withdrawn.
        if product is None:
            raise NotFoundError("Không tìm thấy sản phẩm này.")
        return product
