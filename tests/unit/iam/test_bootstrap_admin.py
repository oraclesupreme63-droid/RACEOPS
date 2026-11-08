"""Unit tests for bootstrap input handling and CLI orchestration."""

from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from raceops.iam import bootstrap_admin
from raceops.iam.bootstrap_admin import BootstrapResult
from raceops.iam.errors import BootstrapConflictError, BootstrapValidationError


def test_bootstrap_normalizes_operator_input() -> None:
    assert bootstrap_admin._normalize_email(" Admin@Example.COM ") == (
        "admin@example.com"
    )
    assert bootstrap_admin._normalize_team_name("  Green Light Racing  ") == (
        "Green Light Racing"
    )


@pytest.mark.parametrize(
    ("value", "normalizer"),
    [
        ("not-an-email", bootstrap_admin._normalize_email),
        ("", bootstrap_admin._normalize_team_name),
        ("x" * 121, bootstrap_admin._normalize_team_name),
    ],
)
def test_bootstrap_rejects_invalid_operator_input(
    value: str,
    normalizer: Any,
) -> None:
    with pytest.raises(BootstrapValidationError):
        normalizer(value)


def test_password_is_read_twice_and_never_accepted_as_cli_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries: Iterator[str] = iter(["long-admin-password", "long-admin-password"])
    monkeypatch.setattr(
        "raceops.iam.bootstrap_admin.getpass.getpass",
        lambda _prompt: next(entries),
    )

    assert bootstrap_admin._read_confirmed_password() == "long-admin-password"

    with pytest.raises(SystemExit):
        bootstrap_admin._build_parser().parse_args(
            [
                "--email",
                "admin@example.com",
                "--team-name",
                "Team",
                "--password",
                "visible-secret",
            ]
        )


def test_mismatched_password_confirmation_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries: Iterator[str] = iter(["long-admin-password", "different-password"])
    monkeypatch.setattr(
        "raceops.iam.bootstrap_admin.getpass.getpass",
        lambda _prompt: next(entries),
    )

    with pytest.raises(BootstrapValidationError, match="does not match"):
        bootstrap_admin._read_confirmed_password()


class _FakeEngine:
    disposed = False

    def dispose(self) -> None:
        self.disposed = True


def test_cli_orchestration_returns_success_without_exposing_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _FakeEngine()
    result = BootstrapResult(uuid4(), uuid4(), uuid4())
    received: dict[str, object] = {}
    settings = SimpleNamespace(log_level="INFO", env="test")

    monkeypatch.setattr(bootstrap_admin, "get_settings", lambda: settings)
    monkeypatch.setattr(bootstrap_admin, "configure_logging", lambda **_kwargs: None)
    monkeypatch.setattr(
        bootstrap_admin, "_read_confirmed_password", lambda: "long-admin-password"
    )
    monkeypatch.setattr(bootstrap_admin, "build_engine", lambda _settings: engine)
    monkeypatch.setattr(
        bootstrap_admin, "build_session_factory", lambda _engine: "factory"
    )

    def fake_bootstrap(factory: object, **values: object) -> BootstrapResult:
        received.update({"factory": factory} | values)
        return result

    monkeypatch.setattr(bootstrap_admin, "bootstrap_administrator", fake_bootstrap)

    exit_code = bootstrap_admin.main(
        ["--email", "admin@example.com", "--team-name", "Race Team"]
    )

    assert exit_code == 0
    assert received["password"] == "long-admin-password"
    assert engine.disposed is True


@pytest.mark.parametrize(
    "error",
    [
        BootstrapConflictError("conflict"),
        BootstrapValidationError("invalid"),
        SQLAlchemyError("database unavailable"),
    ],
)
def test_cli_returns_failure_for_expected_bootstrap_errors(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    engine = _FakeEngine()
    settings = SimpleNamespace(log_level="INFO", env="test")
    monkeypatch.setattr(bootstrap_admin, "get_settings", lambda: settings)
    monkeypatch.setattr(bootstrap_admin, "configure_logging", lambda **_kwargs: None)
    monkeypatch.setattr(
        bootstrap_admin, "_read_confirmed_password", lambda: "long-admin-password"
    )
    monkeypatch.setattr(bootstrap_admin, "build_engine", lambda _settings: engine)
    monkeypatch.setattr(
        bootstrap_admin, "build_session_factory", lambda _engine: "factory"
    )
    monkeypatch.setattr(
        bootstrap_admin,
        "bootstrap_administrator",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )

    assert (
        bootstrap_admin.main(
            ["--email", "admin@example.com", "--team-name", "Race Team"]
        )
        == 1
    )
    assert engine.disposed is True
