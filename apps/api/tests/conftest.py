"""Test fixtures.

The suite runs on SQLite so it needs neither Docker nor a network; the models
use dialect-neutral column types precisely so this stays possible. Migrations
themselves are exercised against Postgres (see `make migrate`).
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("CHART_ENGINE_STAGE", "PREVIEW")

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
async def session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    await engine.dispose()


@pytest.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture
def birth_payload() -> dict[str, object]:
    return {
        "subject_name": "Nguyễn Văn A",
        "gender": "MALE",
        "calendar_type": "SOLAR",
        "birth_day": 10,
        "birth_month": 9,
        "birth_year": 1992,
        "birth_hour": 14,
        "birth_minute": 30,
        "birth_place": "Hà Nội",
        "timezone_name": "Asia/Ho_Chi_Minh",
        "tz_offset": 7,
    }
