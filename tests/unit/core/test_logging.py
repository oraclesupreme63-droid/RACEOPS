"""Unit tests for safe JSON log formatting."""

import json
import logging
import sys

from raceops.core.logging import JsonLogFormatter


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
    record.event = "safe_test_event"
    record.authorization = secret

    serialized = formatter.format(record)
    payload = json.loads(serialized)

    assert payload["event"] == "safe_test_event"
    assert payload["environment"] == "test"
    assert payload["exception_type"] == "RuntimeError"
    assert payload["stack"]
    assert "authorization" not in payload
    assert secret not in serialized
