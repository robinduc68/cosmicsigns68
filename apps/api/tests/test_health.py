from __future__ import annotations

from httpx import AsyncClient


async def test_health_reports_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert body["data"]["status"] == "ok"


async def test_ready_checks_the_database(client: AsyncClient) -> None:
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json()["data"]["checks"]["database"] == "ok"


async def test_every_response_carries_a_request_id(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.headers["X-Request-Id"]


async def test_unknown_route_uses_the_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/khong-ton-tai")
    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
