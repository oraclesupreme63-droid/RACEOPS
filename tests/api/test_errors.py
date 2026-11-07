"""HTTP contracts for request correlation and Problem Details errors."""

import json
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from raceops.main import create_app


@pytest.mark.anyio
async def test_valid_request_id_is_returned_to_the_client() -> None:
    request_id = str(uuid4())
    transport = ASGITransport(app=create_app())

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/health",
            headers={"X-Request-ID": request_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


@pytest.mark.anyio
async def test_invalid_request_id_is_replaced() -> None:
    transport = ASGITransport(app=create_app())

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/health",
            headers={"X-Request-ID": "not-a-valid-request-id"},
        )

    generated = response.headers["X-Request-ID"]
    assert generated != "not-a-valid-request-id"
    assert str(UUID(generated)) == generated


@pytest.mark.anyio
async def test_not_found_uses_problem_details() -> None:
    transport = ASGITransport(app=create_app())

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/does-not-exist")

    body = response.json()
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert body == {
        "type": "https://raceops.local/problems/resource-not-found",
        "title": "Resource not found",
        "status": 404,
        "detail": "The requested resource was not found.",
        "instance": "/does-not-exist",
        "code": "RESOURCE_NOT_FOUND",
        "trace_id": response.headers["X-Request-ID"],
    }


@pytest.mark.anyio
async def test_method_not_allowed_preserves_allow_header() -> None:
    transport = ASGITransport(app=create_app())

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/health")

    assert response.status_code == 405
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["allow"] == "GET"
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"


@pytest.mark.anyio
async def test_validation_problem_does_not_echo_rejected_input() -> None:
    application = create_app()

    @application.get("/api/v1/validation-example")
    async def validation_example(laps: int) -> dict[str, int]:
        return {"laps": laps}

    transport = ASGITransport(app=application)
    rejected_value = "confidential-invalid-value"

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/validation-example",
            params={"laps": rejected_value},
        )

    body = response.json()
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert body["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["trace_id"] == response.headers["X-Request-ID"]
    assert body["errors"][0]["field"] == "query.laps"
    assert body["errors"][0]["code"] == "int_parsing"
    assert rejected_value not in response.text


@pytest.mark.anyio
async def test_access_log_uses_route_template_instead_of_concrete_url(
    capsys: pytest.CaptureFixture[str],
) -> None:
    application = create_app()

    @application.get("/api/v1/vehicles/{vehicle_id}")
    async def get_vehicle(vehicle_id: str) -> dict[str, str]:
        return {"vehicle_id": vehicle_id}

    transport = ASGITransport(app=application)
    concrete_id = "private-vehicle-reference"

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(f"/api/v1/vehicles/{concrete_id}?token=secret")

    output = capsys.readouterr().out
    events = [json.loads(line) for line in output.splitlines() if line]
    access_event = next(
        event for event in events if event["event"] == "http_request_completed"
    )

    assert response.status_code == 200
    assert access_event["route"] == "/api/v1/vehicles/{vehicle_id}"
    assert concrete_id not in output
    assert "token" not in output
    assert "secret" not in output


@pytest.mark.anyio
async def test_unexpected_error_is_safe_and_traceable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    application = create_app()
    secret = "database-password-must-not-leak"

    @application.get("/api/v1/explode")
    async def explode() -> None:
        raise RuntimeError(secret)

    transport = ASGITransport(app=application, raise_app_exceptions=False)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/explode")

    body = response.json()
    output = capsys.readouterr().out
    events = [json.loads(line) for line in output.splitlines() if line]

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert body["code"] == "INTERNAL_SERVER_ERROR"
    assert body["detail"] == "An unexpected error occurred."
    assert body["trace_id"] == response.headers["X-Request-ID"]
    assert secret not in response.text
    assert secret not in output
    assert any(event["event"] == "unhandled_exception" for event in events)
    assert any(
        event["event"] == "http_request_completed"
        and event["request_id"] == body["trace_id"]
        and event["status_code"] == 500
        and event["error_code"] == "INTERNAL_SERVER_ERROR"
        for event in events
    )
