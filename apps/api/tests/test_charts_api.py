from __future__ import annotations

import uuid
from typing import Any

from httpx import AsyncClient


async def _create(client: AsyncClient, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    response = await client.post("/api/v1/charts", json=payload, **kwargs)
    assert response.status_code == 201, response.text
    return response.json()["data"]


async def test_create_chart_returns_the_computed_frame(
    client: AsyncClient, birth_payload: dict[str, Any]
) -> None:
    data = await _create(client, birth_payload)

    assert uuid.UUID(data["id"])
    assert data["subject_name"] == "Nguyễn Văn A"
    chart = data["chart"]
    assert chart["lunar_birth"] == {
        "day": 14,
        "month": 8,
        "year": 1992,
        "is_leap_month": False,
        "year_pillar": "Nhâm Thân",
    }
    assert chart["menh"]["branch"] == "Dần"
    assert chart["cuc"]["label"] == "Kim Tứ Cục"
    assert len(chart["palaces"]) == 12
    assert chart["engine"]["is_authoritative"] is False


async def test_get_chart_by_id(client: AsyncClient, birth_payload: dict[str, Any]) -> None:
    created = await _create(client, birth_payload)
    response = await client.get(f"/api/v1/charts/{created['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created["id"]


async def test_get_unknown_chart_returns_a_friendly_error(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/charts/{uuid.uuid4()}")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert "lá số" in error["message"]


async def test_list_charts_by_ids(client: AsyncClient, birth_payload: dict[str, Any]) -> None:
    first = await _create(client, birth_payload)
    second = await _create(client, {**birth_payload, "subject_name": "Trần Thị B"})

    response = await client.get(f"/api/v1/charts?ids={first['id']},{second['id']},not-a-uuid")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["count"] == 2
    assert {item["id"] for item in body["data"]} == {first["id"], second["id"]}


async def test_delete_chart(client: AsyncClient, birth_payload: dict[str, Any]) -> None:
    created = await _create(client, birth_payload)
    assert (await client.delete(f"/api/v1/charts/{created['id']}")).status_code == 200
    assert (await client.get(f"/api/v1/charts/{created['id']}")).status_code == 404


async def test_repeated_submit_with_the_same_idempotency_key_reuses_the_chart(
    client: AsyncClient, birth_payload: dict[str, Any]
) -> None:
    headers = {"Idempotency-Key": "submit-once"}
    first = await _create(client, birth_payload, headers=headers)
    second = await _create(client, birth_payload, headers=headers)
    assert first["id"] == second["id"]


async def test_lunar_input_is_accepted(client: AsyncClient, birth_payload: dict[str, Any]) -> None:
    data = await _create(
        client,
        {
            **birth_payload,
            "calendar_type": "LUNAR",
            "birth_day": 14,
            "birth_month": 8,
            "birth_year": 1992,
        },
    )
    assert data["chart"]["menh"]["branch"] == "Dần"


async def test_impossible_solar_date_is_rejected(
    client: AsyncClient, birth_payload: dict[str, Any]
) -> None:
    response = await client.post(
        "/api/v1/charts", json={**birth_payload, "birth_day": 31, "birth_month": 2}
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"]["fields"]


async def test_future_birth_date_is_rejected(
    client: AsyncClient, birth_payload: dict[str, Any]
) -> None:
    response = await client.post("/api/v1/charts", json={**birth_payload, "birth_year": 2099})
    assert response.status_code == 422


async def test_missing_required_field_is_rejected(
    client: AsyncClient, birth_payload: dict[str, Any]
) -> None:
    payload = dict(birth_payload)
    del payload["birth_hour"]
    response = await client.post("/api/v1/charts", json=payload)
    assert response.status_code == 422
    assert "birth_hour" in response.json()["error"]["details"]["fields"]


async def test_leap_month_flag_requires_lunar_calendar(
    client: AsyncClient, birth_payload: dict[str, Any]
) -> None:
    response = await client.post("/api/v1/charts", json={**birth_payload, "is_leap_month": True})
    assert response.status_code == 422
