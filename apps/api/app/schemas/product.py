"""Response schemas for the product catalogue."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str
    price_amount: int
    currency: str
    entitlements: list[str]
    is_featured: bool
    sort_order: int
