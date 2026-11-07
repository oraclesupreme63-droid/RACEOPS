"""ASGI middleware for request correlation and safe access logs."""

import logging
from time import perf_counter
from typing import cast

from starlette.datastructures import Headers, MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from raceops.api.errors import INTERNAL_PROBLEM, internal_error_response
from raceops.core.request_context import (
    REQUEST_ID_HEADER,
    bind_request_id,
    create_request_id,
    reset_request_id,
)

logger = logging.getLogger("raceops.http")


class RequestContextMiddleware:
    """Correlate responses and logs without reading request bodies."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = create_request_id(headers.get(REQUEST_ID_HEADER))
        state = scope.setdefault("state", {})
        state["request_id"] = request_id
        token = bind_request_id(request_id)
        started_at = perf_counter()
        status_code = 500
        response_started = False

        async def send_with_request_id(message: Message) -> None:
            nonlocal response_started, status_code
            if message["type"] == "http.response.start":
                response_started = True
                status_code = cast(int, message["status"])
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            try:
                await self._app(scope, receive, send_with_request_id)
            except Exception:
                if response_started:
                    raise

                state["error_code"] = INTERNAL_PROBLEM.code
                logger.exception(
                    "Unhandled request exception",
                    extra={
                        "event": "unhandled_exception",
                        "error_code": INTERNAL_PROBLEM.code,
                    },
                )
                response = internal_error_response(Request(scope))
                await response(scope, receive, send_with_request_id)
        finally:
            duration_ms = round((perf_counter() - started_at) * 1000, 3)
            route = scope.get("route")
            route_template = getattr(route, "path", None) or "<unmatched>"
            error_code = state.get("error_code")
            log_level = logging.ERROR if status_code >= 500 else logging.INFO
            if route_template == "/health" and status_code < 500:
                log_level = logging.DEBUG
            logger.log(
                log_level,
                "HTTP request completed",
                extra={
                    "event": "http_request_completed",
                    "trace_id": request_id,
                    "method": scope["method"],
                    "route": route_template,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "error_code": error_code,
                },
            )
            reset_request_id(token)
