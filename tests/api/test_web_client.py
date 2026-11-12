"""HTTP contract for the packaged validation client."""

from importlib.resources import files

import pytest
from httpx import ASGITransport, AsyncClient

from raceops.core.config import Settings
from raceops.main import create_app


@pytest.mark.anyio
async def test_validation_client_is_served_with_local_assets() -> None:
    app = create_app(Settings(env="test"))
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True,
    ) as client:
        page = await client.get("/app/")
        stylesheet = await client.get("/app/styles.css")
        script = await client.get("/app/app.js")

    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert "Session Learning Loop" in page.text
    assert 'id="login-form"' in page.text
    assert 'id="workspace"' in page.text
    assert 'src="./app.js?v=0.4.0-9.2"' in page.text
    assert 'href="./styles.css?v=0.4.0-9.2"' in page.text

    assert stylesheet.status_code == 200
    assert stylesheet.headers["content-type"].startswith("text/css")
    assert stylesheet.headers["cache-control"] == "no-store"
    assert "prefers-reduced-motion" in stylesheet.text
    assert "@media (max-width: 820px)" in stylesheet.text

    assert script.status_code == 200
    assert script.headers["cache-control"] == "no-store"
    assert "sessionStorage" in script.text
    assert 'const API_BASE = "/api/v1"' in script.text
    assert 'contentType.includes("json")' in script.text
    assert "El correo, la contraseña o el equipo no son válidos." in script.text
    assert "localStorage" not in script.text


def test_validation_client_assets_are_in_the_python_package() -> None:
    web_root = files("raceops").joinpath("web")

    for filename in ("index.html", "styles.css", "app.js"):
        asset = web_root.joinpath(filename)
        assert asset.is_file()
        assert asset.read_text(encoding="utf-8").strip()
