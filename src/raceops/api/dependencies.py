"""HTTP dependency providers."""

from collections.abc import Callable, Iterator
from typing import Annotated, cast

from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, sessionmaker

from raceops.api.errors import ApiProblemError, ProblemDefinition
from raceops.core.config import Settings
from raceops.db.health import DatabaseHealthChecker
from raceops.iam.authorization import Permission, enforce_permission
from raceops.iam.errors import InvalidAccessTokenError
from raceops.iam.identity import CurrentIdentity, resolve_current_identity
from raceops.iam.tokens import decode_access_token

INVALID_ACCESS_TOKEN_PROBLEM = ProblemDefinition(
    "invalid-access-token",
    "Invalid access token",
    "invalid_access_token",
    "The access token is missing, invalid, expired or no longer active.",
)

_bearer_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
    description="Short-lived RaceOps membership access token.",
)


def get_database_health_checker(request: Request) -> DatabaseHealthChecker:
    """Resolve the database health checker owned by the application."""
    return cast(DatabaseHealthChecker, request.app.state.database_health_checker)


def get_settings_from_app(request: Request) -> Settings:
    """Resolve immutable settings owned by the application instance."""
    return cast(Settings, request.app.state.settings)


def get_db_session(request: Request) -> Iterator[Session]:
    """Provide one SQLAlchemy session for one HTTP dependency graph."""
    factory = cast(sessionmaker[Session], request.app.state.db_session_factory)
    with factory() as session:
        yield session


def get_current_identity(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(_bearer_scheme),
    ],
) -> CurrentIdentity:
    """Validate a bearer token and re-resolve its active database identity."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _invalid_access_token_problem()

    settings = get_settings_from_app(request)
    factory = cast(sessionmaker[Session], request.app.state.db_session_factory)
    try:
        claims = decode_access_token(
            token=credentials.credentials,
            secret=settings.jwt_secret.get_secret_value(),
        )
        with factory() as session:
            return resolve_current_identity(session, claims)
    except InvalidAccessTokenError as error:
        raise _invalid_access_token_problem() from error


def require_permission(
    permission: Permission,
) -> Callable[[CurrentIdentity], CurrentIdentity]:
    """Build a FastAPI dependency that returns an authorized current actor."""

    def dependency(
        identity: Annotated[CurrentIdentity, Security(get_current_identity)],
    ) -> CurrentIdentity:
        enforce_permission(identity, permission)
        return identity

    return dependency


def _invalid_access_token_problem() -> ApiProblemError:
    return ApiProblemError(
        status_code=401,
        definition=INVALID_ACCESS_TOKEN_PROBLEM,
        headers={"WWW-Authenticate": "Bearer"},
    )
