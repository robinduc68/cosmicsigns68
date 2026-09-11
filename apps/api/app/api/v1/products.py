"""Product catalogue endpoints.

Read-only and public: the pricing section of the marketing site reads from here
so no price is ever duplicated into the frontend. Editing belongs to the admin
API (Phase 5), not to this router.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import ProductServiceDep
from app.schemas.common import success
from app.schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", summary="Danh sách sản phẩm đang bán")
async def list_products(service: ProductServiceDep) -> dict[str, Any]:
    products = await service.list_active()
    items = [
        ProductOut.model_validate(p, from_attributes=True).model_dump(mode="json")
        for p in products
    ]
    return success(items, {"count": len(items)})


@router.get("/{code}", summary="Xem một sản phẩm")
async def get_product(code: str, service: ProductServiceDep) -> dict[str, Any]:
    product = await service.get_by_code(code)
    return success(
        ProductOut.model_validate(product, from_attributes=True).model_dump(mode="json")
    )
