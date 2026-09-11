"""The internal verification workbench must stay internal.

Only read-only routes are exercised in non-production mode: the write routes
edit the fixture matrix on disk, and a test run must never change the repo.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import AsyncClient

from app.api.v1 import internal_verification

BASE = "/api/v1/_internal/verification"


async def test_the_workbench_is_reachable_outside_production(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/fixtures")
    assert response.status_code == 200
    body = response.json()
    # Counts are derived from the fixture file, so the list and summary must agree.
    assert len(body["data"]) == body["meta"]["summary"]["TOTAL"]


async def test_fixture_detail_keeps_engine_output_and_review_apart(client: AsyncClient) -> None:
    data = (await client.get(f"{BASE}/fixtures/TV-S1")).json()["data"]
    assert data["engine_candidate_stars"]
    assert len(data["comparisons"]) == 14
    # Nothing verified yet: an absent expectation must read UNVERIFIED, never MATCH.
    if data["review"]["expected_stars"] is None:
        assert {row["status"] for row in data["comparisons"]} == {"UNVERIFIED"}


async def test_a_blocked_fixture_is_served_without_building_a_chart(client: AsyncClient) -> None:
    data = (await client.get(f"{BASE}/fixtures/TV-B1")).json()["data"]
    assert data["blocked_reason"]
    assert data["trace"] == []
    assert set(data["late_zi_demonstration"]) == {
        "CIVIL_DAY",
        "LATE_ZI_NEXT_DAY",
        "PILLAR_ONLY_NEXT_DAY",
    }


async def test_the_review_pack_ships_with_blank_expectations(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/export?fmt=csv")
    assert response.status_code == 200
    assert "noindex" in response.headers["x-robots-tag"]
    header, *rows = response.text.strip().splitlines()
    column = header.split(",").index("expected_TU_VI")
    assert all(row.split(",")[column] == "" for row in rows)


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/fixtures"),
        ("GET", "/fixtures/TV-S1"),
        ("GET", "/progress"),
        ("GET", "/sources"),
        ("GET", "/export"),
        ("PUT", "/fixtures/TV-S1/review"),
        ("POST", "/sources"),
        ("POST", "/discrepancies"),
        ("POST", "/import"),
        ("POST", "/promote"),
    ],
)
async def test_every_workbench_route_does_not_exist_in_production(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch, method: str, path: str
) -> None:
    """404, not 403: production should not even admit the surface exists.

    The guard runs before any handler, so write routes are refused before they
    could touch the fixture file.
    """
    monkeypatch.setattr(
        internal_verification, "get_settings", lambda: SimpleNamespace(is_production=True)
    )
    response = await client.request(method, f"{BASE}{path}", json={})
    assert response.status_code == 404


async def test_internal_routes_stay_out_of_the_public_api_schema(client: AsyncClient) -> None:
    paths = (await client.get("/openapi.json")).json()["paths"]
    assert not any("_internal" in path for path in paths)
