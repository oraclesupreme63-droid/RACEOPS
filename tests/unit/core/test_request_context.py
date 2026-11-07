"""Unit tests for request identifier normalization."""

from uuid import UUID, uuid4

from raceops.core.request_context import create_request_id


def test_create_request_id_preserves_only_canonical_uuid() -> None:
    canonical = str(uuid4())

    assert create_request_id(canonical) == canonical


def test_create_request_id_replaces_untrusted_value() -> None:
    generated = create_request_id("../../authorization=secret")

    assert generated != "../../authorization=secret"
    assert str(UUID(generated)) == generated
