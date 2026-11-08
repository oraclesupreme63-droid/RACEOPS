"""Domain errors for identity credentials and access resolution."""


class PasswordPolicyError(ValueError):
    """Raised when a plaintext password violates the documented policy."""


class InvalidAccessTokenError(ValueError):
    """Raised when a token or its current database identity is not valid."""


class BootstrapValidationError(ValueError):
    """Raised before bootstrap persistence when operator input is invalid."""


class BootstrapConflictError(RuntimeError):
    """Raised when bootstrap records conflict with persisted identity data."""
