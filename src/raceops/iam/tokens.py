"""Short-lived JWT access tokens for one selected team membership."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final
from uuid import UUID, uuid4

import jwt
from jwt.exceptions import InvalidTokenError

from raceops.iam.errors import InvalidAccessTokenError

JWT_ALGORITHM: Final = "HS256"
REQUIRED_CLAIMS: Final = ("sub", "mid", "jti", "iat", "exp")


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    """Validated identifiers carried by an access token."""

    user_id: UUID
    membership_id: UUID
    token_id: UUID
    issued_at: datetime
    expires_at: datetime


def issue_access_token(
    *,
    user_id: UUID,
    membership_id: UUID,
    secret: str,
    ttl: timedelta,
    now: datetime | None = None,
    token_id: UUID | None = None,
) -> str:
    """Issue an HS256 token with only stable identity references."""
    if not secret:
        raise ValueError("JWT secret must not be empty")
    if ttl <= timedelta(0):
        raise ValueError("access token TTL must be positive")

    issued_at = _as_utc(now or datetime.now(UTC))
    expires_at = issued_at + ttl
    payload = {
        "sub": str(user_id),
        "mid": str(membership_id),
        "jti": str(token_id or uuid4()),
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(*, token: str, secret: str) -> AccessTokenClaims:
    """Verify signature, expiration, required claims, and UUID claim shapes."""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[JWT_ALGORITHM],
            options={"require": list(REQUIRED_CLAIMS)},
        )
        user_id = UUID(_required_string(payload, "sub"))
        membership_id = UUID(_required_string(payload, "mid"))
        token_id = UUID(_required_string(payload, "jti"))
        issued_at = datetime.fromtimestamp(_required_int(payload, "iat"), UTC)
        expires_at = datetime.fromtimestamp(_required_int(payload, "exp"), UTC)
    except (InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise InvalidAccessTokenError("access token is invalid") from error

    if expires_at <= issued_at:
        raise InvalidAccessTokenError("access token is invalid")

    return AccessTokenClaims(
        user_id=user_id,
        membership_id=membership_id,
        token_id=token_id,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def _required_string(payload: dict[str, object], claim: str) -> str:
    value = payload[claim]
    if not isinstance(value, str) or not value:
        raise TypeError(f"{claim} must be a non-empty string")
    return value


def _required_int(payload: dict[str, object], claim: str) -> int:
    value = payload[claim]
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{claim} must be an integer")
    return value


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("token timestamps must be timezone-aware")
    return value.astimezone(UTC)
