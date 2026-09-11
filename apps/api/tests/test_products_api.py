from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models.product import Product


@pytest.fixture
async def catalogue(session_factory: async_sessionmaker[AsyncSession]) -> None:
    """A catalogue shaped like the seeded one, plus a withdrawn product.

    The suite builds its schema with ``create_all`` rather than by running
    migrations, so the seeded rows are not here — tests insert what they need.
    """
    async with session_factory() as session:
        session.add_all(
            [
                Product(
                    code="LOVE_READING",
                    name="Tình yêu & Hôn nhân",
                    description="Đọc từ cung Phu Thê.",
                    price_amount=99000,
                    entitlements=["LOVE_READING"],
                    sort_order=30,
                ),
                Product(
                    code="FULL_LIFETIME_READING",
                    name="Trọn đời",
                    description="Toàn bộ các phần luận giải.",
                    price_amount=250000,
                    entitlements=["FULL_LIFETIME_READING", "PDF_EXPORT"],
                    is_featured=True,
                    sort_order=40,
                ),
                Product(
                    code="EARLY_BIRD",
                    name="Gói ra mắt",
                    description="Đã ngừng bán.",
                    price_amount=49000,
                    entitlements=["FULL_LIFETIME_READING"],
                    is_active=False,
                    sort_order=5,
                ),
            ]
        )
        await session.commit()


async def test_list_returns_active_products_in_display_order(
    client: AsyncClient, catalogue: None
) -> None:
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    body = response.json()

    codes = [item["code"] for item in body["data"]]
    # EARLY_BIRD is withdrawn: it must not reach the pricing page even though its
    # sort_order would otherwise place it first.
    assert codes == ["LOVE_READING", "FULL_LIFETIME_READING"]
    assert body["meta"]["count"] == 2


async def test_list_exposes_the_fields_the_pricing_page_needs(
    client: AsyncClient, catalogue: None
) -> None:
    data = (await client.get("/api/v1/products")).json()["data"]
    full = next(item for item in data if item["code"] == "FULL_LIFETIME_READING")

    assert uuid.UUID(full["id"])
    assert full["price_amount"] == 250000
    assert full["currency"] == "VND"
    assert full["is_featured"] is True
    # Buying the lifetime product grants more than its own code.
    assert full["entitlements"] == ["FULL_LIFETIME_READING", "PDF_EXPORT"]


async def test_price_is_a_whole_number_of_dong(client: AsyncClient, catalogue: None) -> None:
    data = (await client.get("/api/v1/products")).json()["data"]
    # Money must never arrive as a float — rounding it would be a real loss.
    assert all(isinstance(item["price_amount"], int) for item in data)


async def test_get_by_code_still_resolves_a_withdrawn_product(
    client: AsyncClient, catalogue: None
) -> None:
    # An order placed while it was on sale has to stay explainable afterwards.
    response = await client.get("/api/v1/products/EARLY_BIRD")
    assert response.status_code == 200
    assert response.json()["data"]["code"] == "EARLY_BIRD"


async def test_get_by_unknown_code_is_a_404(client: AsyncClient, catalogue: None) -> None:
    response = await client.get("/api/v1/products/KHONG_CO_THAT")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


async def test_list_is_empty_rather_than_failing_when_nothing_is_on_sale(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.json()["data"] == []
