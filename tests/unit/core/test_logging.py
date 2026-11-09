"""Unit tests for safe JSON log formatting."""

import json
import logging
import sys

import pytest

from raceops.core.logging import (
    DynamicStdoutHandler,
    JsonLogFormatter,
    configure_logging,
)


def test_json_formatter_uses_an_allowlist_and_redacts_exception_message() -> None:
    formatter = JsonLogFormatter(environment="test")
    secret = "Bearer private-token"

    try:
        raise RuntimeError(secret)
    except RuntimeError:
        exception_info = sys.exc_info()

    record = logging.LogRecord(
        name="raceops.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="Safe diagnostic message",
        args=(),
        exc_info=exception_info,
    )
    driver_id = "5e122f1a-1fe8-4d4e-aabc-56313c0c101b"
    record.event = "safe_test_event"
    record.__dict__["driver_id"] = driver_id
    record.__dict__["driver_status"] = "ACTIVE"
    record.authorization = secret

    serialized = formatter.format(record)
    payload = json.loads(serialized)

    assert payload["event"] == "safe_test_event"
    assert payload["environment"] == "test"
    assert payload["exception_type"] == "RuntimeError"
    assert payload["stack"]
    assert payload["driver_id"] == driver_id
    assert payload["driver_status"] == "ACTIVE"
    assert "authorization" not in payload
    assert secret not in serialized


def test_dynamic_handler_uses_current_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    handler = DynamicStdoutHandler()
    handler.setFormatter(JsonLogFormatter(environment="test"))
    record = logging.LogRecord(
        name="raceops.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Current stdout",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    payload = json.loads(capsys.readouterr().out)

    assert payload["message"] == "Current stdout"


def test_configure_logging_reenables_raceops_namespace() -> None:
    raceops_logger = logging.getLogger("raceops")
    child_logger = logging.getLogger("raceops.http")
    raceops_logger.disabled = True
    child_logger.disabled = True

    configure_logging(level="INFO", environment="test")

    assert raceops_logger.disabled is False
    assert child_logger.disabled is False
