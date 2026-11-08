"""Safe structured logging configuration for RaceOps."""

import json
import logging
import sys
import traceback
from datetime import UTC, datetime
from types import TracebackType
from typing import Final

from raceops.core.request_context import get_current_request_id

SERVICE_NAME: Final = "raceops-api"

_STRUCTURED_FIELDS: Final = (
    "trace_id",
    "method",
    "route",
    "status_code",
    "duration_ms",
    "error_code",
    "user_id",
    "membership_id",
    "team_id",
    "auth_failure_reason",
)


class JsonLogFormatter(logging.Formatter):
    """Serialize an allowlist of diagnostic fields as one JSON object."""

    def __init__(self, environment: str) -> None:
        super().__init__()
        self._environment = environment

    def format(self, record: logging.LogRecord) -> str:
        """Create a stable log event without serializing arbitrary extras."""
        request_id = getattr(record, "request_id", None) or get_current_request_id()
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "environment": self._environment,
            "event": getattr(record, "event", record.name),
            "message": record.getMessage(),
        }

        if request_id is not None:
            payload["request_id"] = request_id

        for field in _STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info is not None:
            exception_type, _, exception_traceback = record.exc_info
            if exception_type is not None:
                payload["exception_type"] = exception_type.__name__
            payload["stack"] = _safe_stack(exception_traceback)

        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def _safe_stack(exception_traceback: TracebackType | None) -> list[dict[str, object]]:
    """Return stack locations without exception messages or local values."""
    if exception_traceback is None:
        return []

    return [
        {
            "file": frame.filename,
            "line": frame.lineno,
            "function": frame.name,
        }
        for frame in traceback.extract_tb(exception_traceback)
    ]


def configure_logging(*, level: str, environment: str) -> None:
    """Configure the RaceOps logger without replacing third-party handlers."""
    raceops_logger = logging.getLogger("raceops")
    raceops_logger.setLevel(level)
    raceops_logger.propagate = False

    for handler in list(raceops_logger.handlers):
        if getattr(handler, "_raceops_handler", False):
            raceops_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter(environment))
    handler._raceops_handler = True  # type: ignore[attr-defined]
    raceops_logger.addHandler(handler)
