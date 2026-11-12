"""Packaged, buildless validation client served by the RaceOps process."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, Response

router = APIRouter(include_in_schema=False)
_WEB_DIRECTORY = Path(__file__).with_name("web")
_INDEX = (_WEB_DIRECTORY / "index.html").read_text(encoding="utf-8")
_STYLES = (_WEB_DIRECTORY / "styles.css").read_text(encoding="utf-8")
_SCRIPT = (_WEB_DIRECTORY / "app.js").read_text(encoding="utf-8")


@router.get("/app", response_class=RedirectResponse)
def redirect_validation_client() -> RedirectResponse:
    """Normalize the entry URL so its relative assets resolve predictably."""
    return RedirectResponse(url="/app/", status_code=307)


@router.get("/app/", response_class=HTMLResponse)
def validation_client() -> HTMLResponse:
    """Return the validation UI without external frontend infrastructure."""
    return HTMLResponse(
        _INDEX,
        headers={"Cache-Control": "no-store"},
    )


@router.get("/app/styles.css")
def validation_client_styles() -> Response:
    """Return the responsive presentation layer as a packaged asset."""
    return Response(
        _STYLES,
        media_type="text/css",
        headers={"Cache-Control": "no-store"},
    )


@router.get("/app/app.js")
def validation_client_script() -> Response:
    """Return the thin API client as a packaged asset."""
    return Response(
        _SCRIPT,
        media_type="text/javascript",
        headers={"Cache-Control": "no-store"},
    )
