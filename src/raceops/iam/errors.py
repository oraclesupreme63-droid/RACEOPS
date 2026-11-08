"""Domain errors for identity credentials and access resolution."""

from uuid import UUID


class PasswordPolicyError(ValueError):
    """Raised when a plaintext password violates the documented policy."""


class InvalidAccessTokenError(ValueError):
    """Raised when a token or its current database identity is not valid."""


class BootstrapValidationError(ValueError):
    """Raised before bootstrap persistence when operator input is invalid."""


class BootstrapConflictError(RuntimeError):
    """Raised when bootstrap records conflict with persisted identity data."""


class InvalidCredentialsError(ValueError):
    """Raised for every externally indistinguishable login rejection."""

    def __init__(self, reason: str) -> None:
        super().__init__("credentials are invalid")
        self.reason = reason


class TeamContextRequiredError(ValueError):
    """Raised after valid credentials when one active team must be selected."""

    def __init__(self, teams: tuple[tuple[UUID, str], ...]) -> None:
        super().__init__("team context is required")
        self.teams = teams


class InsufficientPermissionsError(PermissionError):
    """Raised when an authenticated role lacks an explicit permission."""


class ResourceNotFoundError(LookupError):
    """Raised when a resource is absent or must be hidden from the actor."""
