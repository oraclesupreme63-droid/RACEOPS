"""Unit tests for the frozen validation scenario and safe CLI input."""

from unittest.mock import Mock

import pytest
from pydantic import SecretStr

from raceops.core.config import Settings
from raceops.sessions.enums import LapClassification, SectorStatus
from raceops.validation import seed_scenario
from raceops.validation.scenario import load_validation_scenario
from raceops.validation.seed_scenario import ValidationScenarioError


def test_frozen_scenario_contains_uncertainty_and_partial_data() -> None:
    scenario = load_validation_scenario()

    assert scenario.version == "phase-9-v1"
    assert scenario.source_session.conditions.track_temperature is None
    assert any(
        lap.classification is LapClassification.INVALID
        for lap in scenario.source_session.laps
    )
    assert any(
        sector.status is SectorStatus.INCOMPLETE
        for lap in scenario.source_session.laps
        for sector in lap.sectors
    )
    assert scenario.rehearsal["hypothesis"]


def test_public_dataset_preserves_source_boundary_and_exact_sector_totals() -> None:
    scenario = load_validation_scenario("public-kristianstad-2025")

    assert scenario.version == "phase-9-public-v1"
    assert scenario.event_end_date is not None
    assert scenario.published_source is not None
    assert scenario.published_source.source_type == "PUBLIC_TIMING"
    assert scenario.driver_name == "Public Driver 027"
    assert len(scenario.source_session.laps) == 13
    assert len(scenario.evaluation_session.laps) == 25

    all_laps = scenario.source_session.laps + scenario.evaluation_session.laps
    assert all(len(lap.sectors) == 3 for lap in all_laps)
    assert all(
        sum(sector.duration_us for sector in lap.sectors) == lap.duration_us
        for lap in all_laps
    )

    source_best = min(lap.duration_us for lap in scenario.source_session.laps)
    evaluation_best = min(lap.duration_us for lap in scenario.evaluation_session.laps)
    assert source_best == 50_368_000
    assert evaluation_best == 50_348_000
    assert evaluation_best - source_best == -20_000


def test_public_dataset_is_available_from_cli() -> None:
    options = seed_scenario._build_parser().parse_args(
        [
            "--scenario-id",
            "public-round",
            "--dataset",
            "public-kristianstad-2025",
        ]
    )

    assert options.dataset == "public-kristianstad-2025"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(" Round-1 ", "round-1"), ("pilot02", "pilot02")],
)
def test_scenario_id_is_normalized(raw: str, expected: str) -> None:
    assert seed_scenario._normalize_scenario_id(raw) == expected


@pytest.mark.parametrize("value", ["x", "bad id", "bad_underscore", "-round"])
def test_scenario_id_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(ValidationScenarioError):
        seed_scenario._normalize_scenario_id(value)


def test_password_confirmation_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(("first-local-password", "different-local-password"))
    monkeypatch.setattr(
        "raceops.validation.seed_scenario.getpass.getpass",
        lambda _prompt: next(answers),
    )

    with pytest.raises(ValidationScenarioError, match="confirmation"):
        seed_scenario._read_confirmed_password()


def test_seed_service_refuses_non_local_environment() -> None:
    session_factory = Mock()

    with pytest.raises(ValidationScenarioError, match="local or test"):
        seed_scenario.seed_validation_scenario(
            session_factory=session_factory,
            environment="production",
            scenario_id="round-1",
            password="unused-production-password",
        )

    session_factory.assert_not_called()


def test_cli_refuses_production_before_reading_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        env="production",
        database_url=SecretStr(
            "postgresql+psycopg://secure:secure@database.internal/raceops"
        ),
        jwt_secret=SecretStr("a-production-secret-longer-than-thirty-two-chars"),
    )
    read_password = Mock()
    monkeypatch.setattr(seed_scenario, "get_settings", lambda: settings)
    monkeypatch.setattr(seed_scenario, "configure_logging", lambda **_kwargs: None)
    monkeypatch.setattr(seed_scenario, "_read_confirmed_password", read_password)

    assert seed_scenario.main(["--scenario-id", "round-1"]) == 1
    read_password.assert_not_called()
