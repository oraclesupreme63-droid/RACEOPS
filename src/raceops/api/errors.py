"""RFC 9457 Problem Details responses for the HTTP boundary."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from raceops.core.request_context import create_request_id

PROBLEM_TYPE_BASE = "https://raceops.local/problems"


class FieldError(BaseModel):
    """Safe description of one invalid request field."""

    field: str
    code: str
    message: str


class ProblemDetails(BaseModel):
    """RaceOps extension of the RFC 9457 response object."""

    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    trace_id: str
    errors: list[FieldError] | None = None


@dataclass(frozen=True)
class ProblemDefinition:
    """Safe public representation for an HTTP failure category."""

    slug: str
    title: str
    code: str
    detail: str


HTTP_PROBLEMS: Mapping[int, ProblemDefinition] = {
    400: ProblemDefinition(
        "bad-request",
        "Bad request",
        "BAD_REQUEST",
        "The request could not be processed.",
    ),
    401: ProblemDefinition(
        "authentication-required",
        "Authentication required",
        "AUTHENTICATION_REQUIRED",
        "Valid authentication is required to access this resource.",
    ),
    403: ProblemDefinition(
        "forbidden",
        "Forbidden",
        "FORBIDDEN",
        "You are not allowed to perform this operation.",
    ),
    404: ProblemDefinition(
        "resource-not-found",
        "Resource not found",
        "RESOURCE_NOT_FOUND",
        "The requested resource was not found.",
    ),
    405: ProblemDefinition(
        "method-not-allowed",
        "Method not allowed",
        "METHOD_NOT_ALLOWED",
        "The HTTP method is not allowed for this resource.",
    ),
    409: ProblemDefinition(
        "conflict",
        "Conflict",
        "CONFLICT",
        "The operation conflicts with the current resource state.",
    ),
}

VALIDATION_PROBLEM = ProblemDefinition(
    "request-validation-error",
    "Request validation failed",
    "REQUEST_VALIDATION_ERROR",
    "One or more request fields are invalid.",
)

INTERNAL_PROBLEM = ProblemDefinition(
    "internal-server-error",
    "Internal server error",
    "INTERNAL_SERVER_ERROR",
    "An unexpected error occurred.",
)


def register_exception_handlers(application: FastAPI) -> None:
    """Install the expected HTTP and request-validation translators."""
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )


async def http_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Translate framework HTTP exceptions to a stable public contract."""
    if not isinstance(exception, HTTPException):
        raise exception

    definition = HTTP_PROBLEMS.get(
        exception.status_code,
        ProblemDefinition(
            "http-error",
            "HTTP error",
            "HTTP_ERROR",
            "The request could not be completed.",
        ),
    )
    return problem_response(
        request=request,
        status_code=exception.status_code,
        definition=definition,
        headers=exception.headers,
    )


async def validation_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Translate Pydantic failures without echoing rejected input values."""
    if not isinstance(exception, RequestValidationError):
        raise exception

    errors = [
        FieldError(
            field=".".join(str(part) for part in error["loc"]),
            code=str(error["type"]),
            message=str(error["msg"]),
        )
        for error in exception.errors()
    ]
    return problem_response(
        request=request,
        status_code=422,
        definition=VALIDATION_PROBLEM,
        errors=errors,
    )


def internal_error_response(request: Request) -> JSONResponse:
    """Create the generic response for an unexpected server exception."""
    return problem_response(
        request=request,
        status_code=500,
        definition=INTERNAL_PROBLEM,
    )


def problem_response(
    *,
    request: Request,
    status_code: int,
    definition: ProblemDefinition,
    errors: list[FieldError] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build one RFC 9457 response and expose its code to request logging."""
    request_id = _request_id_from(request)
    request.state.error_code = definition.code
    problem = ProblemDetails(
        type=f"{PROBLEM_TYPE_BASE}/{definition.slug}",
        title=definition.title,
        status=status_code,
        detail=definition.detail,
        instance=request.url.path,
        code=definition.code,
        trace_id=request_id,
        errors=errors,
    )
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(exclude_none=True),
        headers=dict(headers) if headers is not None else None,
        media_type="application/problem+json",
    )


def _request_id_from(request: Request) -> str:
    request_id: Any = getattr(request.state, "request_id", None)
    if isinstance(request_id, str):
        return request_id

    generated = create_request_id()
    request.state.request_id = generated
    return generated
