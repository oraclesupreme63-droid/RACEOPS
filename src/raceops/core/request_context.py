"""Per-request correlation context."""

from contextvars import ContextVar, Token
from uuid import UUID, uuid4

REQUEST_ID_HEADER = "X-Request-ID"

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def create_request_id(candidate: str | None = None) -> str:
    """Return a canonical UUID, preserving only valid incoming identifiers."""
    if candidate is not None:
        try:
            parsed = UUID(candidate)
        except (ValueError, AttributeError):
            pass
        else:
            canonical = str(parsed)
            if candidate.lower() == canonical:
                return canonical

    return str(uuid4())


def bind_request_id(request_id: str) -> Token[str | None]:
    """Bind a request ID to the current asynchronous context."""
    return _request_id.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    """Restore the correlation context that preceded the request."""
    _request_id.reset(token)


def get_current_request_id() -> str | None:
    """Return the request ID bound to the current context, when present."""
    return _request_id.get()
