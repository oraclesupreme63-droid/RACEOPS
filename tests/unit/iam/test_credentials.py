"""Unit tests for the explicit RaceOps password policy."""

import pytest

from raceops.iam.credentials import hash_password, validate_password, verify_password
from raceops.iam.errors import PasswordPolicyError


def test_argon2id_hash_never_contains_plaintext_and_verifies_full_password() -> None:
    password = "correct horse battery staple"

    password_hash = hash_password(password)

    assert password_hash.startswith("$argon2id$")
    assert password not in password_hash
    assert verify_password(password, password_hash) is True
    assert verify_password(f"{password}!", password_hash) is False


@pytest.mark.parametrize("password", ["short", "x" * 129])
def test_password_policy_rejects_outside_documented_limits(password: str) -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password(password)


def test_password_policy_counts_unicode_characters_without_truncation() -> None:
    password = "🏁" * 128

    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True
    assert verify_password(f"{password}🏁", password_hash) is False


def test_verification_rejects_malformed_hash_and_invalid_candidate() -> None:
    assert verify_password("long-enough-password", "not-a-supported-hash") is False
    assert verify_password("short", hash_password("long-enough-password")) is False
