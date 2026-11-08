"""HTTP boundary for RaceOps authentication and current identity."""

import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import (
    get_current_identity,
    get_db_session,
    get_settings_from_app,
)
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.core.config import Settings
from raceops.iam.authentication import authenticate_credentials
from raceops.iam.errors import InvalidCredentialsError, TeamContextRequiredError
from raceops.iam.identity import CurrentIdentity
from raceops.iam.schemas import (
    AccessTokenResponse,
    CurrentIdentityResponse,
    LoginRequest,
    TeamChoice,
    TeamContextProblemDetails,
)
from raceops.iam.tokens import issue_access_token

logger = logging.getLogger("raceops.iam.auth")
router = APIRouter(prefix="/auth", tags=["identity"])

INVALID_CREDENTIALS_PROBLEM = ProblemDefinition(
    "invalid-credentials",
    "Invalid credentials",
    "invalid_credentials",
    "The supplied credentials or team context are invalid.",
)
TEAM_CONTEXT_REQUIRED_PROBLEM = ProblemDefinition(
    "team-context-required",
    "Team context required",
    "team_context_required",
    "Select one active team to continue.",
)


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and select a team context",
    responses={
        401: {"model": ProblemDetails, "description": "Invalid credentials."},
        409: {
            "model": TeamContextProblemDetails,
            "description": "Valid credentials require a team selection.",
        },
        422: {"model": ProblemDetails, "description": "Invalid request payload."},
    },
)
def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings_from_app)],
) -> AccessTokenResponse:
    """Issue one short-lived token for one active TeamMembership."""
    try:
        authenticated = authenticate_credentials(
            session,
            email=payload.email,
            password=payload.password,
            team_id=payload.team_id,
        )
    except InvalidCredentialsError as error:
        logger.warning(
            "login rejected",
            extra={
                "event": "identity.login_rejected",
                "auth_failure_reason": error.reason,
            },
        )
        raise ApiProblemError(
            status_code=401,
            definition=INVALID_CREDENTIALS_PROBLEM,
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except TeamContextRequiredError as error:
        teams = [
            TeamChoice(team_id=team_id, name=name) for team_id, name in error.teams
        ]
        logger.info(
            "team context required",
            extra={"event": "identity.team_context_required"},
        )
        raise ApiProblemError(
            status_code=409,
            definition=TEAM_CONTEXT_REQUIRED_PROBLEM,
            extensions={
                "teams": [team.model_dump(mode="json") for team in teams],
            },
        ) from error

    token = issue_access_token(
        user_id=authenticated.user_id,
        membership_id=authenticated.membership_id,
        secret=settings.jwt_secret.get_secret_value(),
        ttl=timedelta(minutes=settings.access_token_ttl_minutes),
    )
    logger.info(
        "login completed",
        extra={
            "event": "identity.login_completed",
            "user_id": str(authenticated.user_id),
            "membership_id": str(authenticated.membership_id),
            "team_id": str(authenticated.team_id),
        },
    )
    return AccessTokenResponse(
        access_token=token,
        expires_in=settings.access_token_ttl_minutes * 60,
    )


@router.get(
    "/me",
    response_model=CurrentIdentityResponse,
    summary="Read the current database-backed identity",
    responses={
        401: {
            "model": ProblemDetails,
            "description": "Missing, invalid, expired or inactive access token.",
        }
    },
)
def get_me(
    identity: Annotated[CurrentIdentity, Depends(get_current_identity)],
) -> CurrentIdentityResponse:
    """Return the active User, Team, Membership and current Role."""
    return CurrentIdentityResponse.from_current_identity(identity)
