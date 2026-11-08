"""Password policy, hashing, and verification."""

from typing import Final

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from raceops.iam.errors import PasswordPolicyError

MIN_PASSWORD_LENGTH: Final = 12
MAX_PASSWORD_LENGTH: Final = 128

_password_hash = PasswordHash.recommended()


def validate_password(password: str) -> None:
    """Reject passwords outside the explicit Unicode character limits."""
    password_length = len(password)
    if password_length < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"password must contain at least {MIN_PASSWORD_LENGTH} characters"
        )
    if password_length > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"password must contain at most {MAX_PASSWORD_LENGTH} characters"
        )


def hash_password(password: str) -> str:
    """Validate and hash a complete password with recommended Argon2id settings."""
    validate_password(password)
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify the complete candidate without silently truncating it."""
    try:
        validate_password(password)
        return _password_hash.verify(password, password_hash)
    except (PasswordPolicyError, UnknownHashError):
        return False
