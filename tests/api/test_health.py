"""HTTP contract tests for the process health endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from raceops import __version__
from raceops.main import create_app


@pytest.mark.anyio
async def test_health_returns_stable_contract() -> None:
    transport = ASGITransport(app=create_app())

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {
        "status": "ok",
        "service": "raceops-api",
        "version": __version__,
    }


@pytest.mark.anyio
async def test_health_is_documented_in_openapi() -> None:
    transport = ASGITransport(app=create_app())

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    document = response.json()
    assert document["info"]["title"] == "RaceOps API"
    assert document["info"]["version"] == __version__
    assert "/health" in document["paths"]
