"""Contract tests for the static dashboard per docs/specs/frontend.md."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_contains_form_and_script():
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="repo-form"' in response.text
    assert "/static/app.js" in response.text
    assert "/static/style.css" in response.text


def test_static_assets_are_served():
    js = client.get("/static/app.js")
    assert js.status_code == 200
    assert "repo-form" in js.text

    css = client.get("/static/style.css")
    assert css.status_code == 200
    assert "banner" in css.text
