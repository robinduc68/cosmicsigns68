"""Chart endpoints.

Charts are addressed by UUID only. Until authentication lands (Phase 4) a chart
is owned by whoever holds its id, which is why the id must stay unguessable.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Header, Query, status

from app.api.deps import ChartServiceDep
from app.schemas.chart import ChartCreateRequest, ChartDetail, ChartSummary
from app.schemas.common import success

router = APIRouter(prefix="/charts", tags=["charts"])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Lập lá số")
async def create_chart(
    payload: ChartCreateRequest,
    service: ChartServiceDep,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, Any]:
    chart = await service.create(payload, idempotency_key)
    return success(ChartDetail.model_validate(chart, from_attributes=True).model_dump(mode="json"))


@router.get("", summary="Lấy nhiều lá số theo id")
async def list_charts(
    service: ChartServiceDep,
    ids: Annotated[str, Query(description="Danh sách id, phân tách bằng dấu phẩy")] = "",
) -> dict[str, Any]:
    parsed: list[uuid.UUID] = []
    for raw in ids.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            parsed.append(uuid.UUID(raw))
        except ValueError:  # ignore junk ids instead of failing the whole list
            continue
    charts = await service.list_by_ids(parsed[:50])
    return success(
        [
            ChartSummary.model_validate(c, from_attributes=True).model_dump(mode="json")
            for c in charts
        ],
        {"count": len(charts)},
    )


@router.get("/{chart_id}", summary="Xem một lá số")
async def get_chart(chart_id: uuid.UUID, service: ChartServiceDep) -> dict[str, Any]:
    chart = await service.get(chart_id)
    return success(ChartDetail.model_validate(chart, from_attributes=True).model_dump(mode="json"))


@router.delete("/{chart_id}", status_code=status.HTTP_200_OK, summary="Xóa lá số")
async def delete_chart(chart_id: uuid.UUID, service: ChartServiceDep) -> dict[str, Any]:
    await service.delete(chart_id)
    return success({"deleted": True, "id": str(chart_id)})
