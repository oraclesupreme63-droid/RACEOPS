"""Versioned business API router."""

from fastapi import APIRouter

from raceops.iam.router import router as identity_router
from raceops.operations.context_router import router as context_router
from raceops.operations.router import router as operations_router
from raceops.sessions.results_router import router as results_router
from raceops.sessions.router import router as sessions_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(identity_router)
api_router.include_router(operations_router)
api_router.include_router(context_router)
api_router.include_router(sessions_router)
api_router.include_router(results_router)
