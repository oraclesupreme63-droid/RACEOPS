"""Unit tests for short-lived membership-scoped access tokens."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from raceops.iam.errors import InvalidAccessTokenError
from raceops.iam.tokens import (
    JWT_ALGORITHM,
    decode_access_token,
    issue_access_token,
)

SECRET = "unit-test-secret-that-is-never-deployed"


def test_access_token_round_trip_contains_only_identity_references() -> None:
    user_id = uuid4()
    membership_id = uuid4()
    token_id = uuid4()
    now = datetime.now(UTC).replace(microsecond=0)

    token = issue_access_token(
        user_id=user_id,
        membership_id=membership_id,
        secret=SECRET,
        ttl=timedelta(minutes=15),
        now=now,
        token_id=token_id,
    )
    claims = decode_access_token(token=token, secret=SECRET)
    raw_payload = jwt.decode(token, SECRET, algorithms=[JWT_ALGORITHM])

    assert claims.user_id == user_id
    assert claims.membership_id == membership_id
    assert claims.token_id == token_id
    assert claims.issued_at == now
    assert claims.expires_at == now + timedelta(minutes=15)
    assert set(raw_payload) == {"sub", "mid", "jti", "iat", "exp"}


def test_expired_and_tampered_tokens_are_rejected() -> None:
    expired_token = issue_access_token(
        user_id=uuid4(),
        membership_id=uuid4(),
        secret=SECRET,
        ttl=timedelta(minutes=1),
        now=datetime.now(UTC) - timedelta(minutes=2),
    )
    valid_token = issue_access_token(
        user_id=uuid4(),
        membership_id=uuid4(),
        secret=SECRET,
        ttl=timedelta(minutes=15),
    )
    tampered_token = f"{valid_token[:-1]}{'a' if valid_token[-1] != 'a' else 'b'}"

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token=expired_token, secret=SECRET)
    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token=tampered_token, secret=SECRET)


@pytest.mark.parametrize(
    "payload",
    [
        {"sub": str(uuid4()), "mid": str(uuid4()), "iat": 1, "exp": 2},
        {
            "sub": "not-a-uuid",
            "mid": str(uuid4()),
            "jti": str(uuid4()),
            "iat": 1,
            "exp": 4_102_444_800,
        },
        {
            "sub": str(uuid4()),
            "mid": str(uuid4()),
            "jti": str(uuid4()),
            "iat": 4_102_444_800,
            "exp": 4_102_444_799,
        },
    ],
)
def test_required_claims_and_claim_shapes_are_enforced(
    payload: dict[str, object],
) -> None:
    token = jwt.encode(payload, SECRET, algorithm=JWT_ALGORITHM)

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token=token, secret=SECRET)


def test_token_issuer_rejects_unsafe_inputs() -> None:
    user_id = uuid4()
    membership_id = uuid4()

    with pytest.raises(ValueError, match="secret"):
        issue_access_token(
            user_id=user_id,
            membership_id=membership_id,
            secret="",
            ttl=timedelta(minutes=15),
        )
    with pytest.raises(ValueError, match="positive"):
        issue_access_token(
            user_id=user_id,
            membership_id=membership_id,
            secret=SECRET,
            ttl=timedelta(0),
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        issue_access_token(
            user_id=user_id,
            membership_id=membership_id,
            secret=SECRET,
            ttl=timedelta(minutes=15),
            now=datetime(2026, 1, 1),
        )
