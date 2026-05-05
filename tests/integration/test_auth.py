import pytest
from httpx import AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_healthz() -> None:
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_unknown_provider_returns_400() -> None:
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/auth/unknown_provider")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_me_without_token_returns_401() -> None:
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/auth/me")
    assert response.status_code == 401
