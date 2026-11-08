"""HTTP contract tests for the process health endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from raceops import __version__
from raceops.core.config import Settings
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


@pytest.mark.anyio
async def test_cors_allows_only_configured_origins_and_exposes_request_id() -> None:
    allowed_origin = "https://app.raceops.example"
    application = create_app(Settings(cors_origins=[allowed_origin]))
    transport = ASGITransport(app=application)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        allowed = await client.get("/health", headers={"Origin": allowed_origin})
        denied = await client.get(
            "/health",
            headers={"Origin": "https://untrusted.example"},
        )
        preflight = await client.options(
            "/api/v1/auth/me",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

    assert allowed.headers["access-control-allow-origin"] == allowed_origin
    assert allowed.headers["access-control-expose-headers"] == "X-Request-ID"
    assert "access-control-allow-origin" not in denied.headers
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == allowed_origin
    assert "Authorization" in preflight.headers["access-control-allow-headers"]
