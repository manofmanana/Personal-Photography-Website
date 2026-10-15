import os
import re
import shutil
import sqlite3

import pytest

os.environ.setdefault("ADMIN_PASSWORD", "test-password")

import app as site  # noqa: E402  (ADMIN_PASSWORD must be set before import)


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Test client backed by a throwaway copy of the database."""
    db_copy = tmp_path / "database.db"
    shutil.copy(site.DB_PATH, db_copy)
    monkeypatch.setattr(site, "DB_PATH", str(db_copy))
    site.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    yield site.app.test_client()
    site.app.config.update(WTF_CSRF_ENABLED=True)


def login(client, password="test-password"):
    return client.post("/admin/login", data={"password": password})


def count_subscribers():
    with sqlite3.connect(site.DB_PATH) as db:
        return db.execute("SELECT count(*) FROM subscribers").fetchone()[0]


@pytest.mark.parametrize("path", ["/", "/gallery", "/services", "/blog", "/about", "/contact", "/contact?type=graduation", "/search", "/search?q=photo", "/search?q=zzzz-no-match", "/post/6"])
def test_public_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_missing_post_redirects_to_blog(client):
    response = client.get("/post/999999")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/blog")


@pytest.mark.parametrize("path", ["/admin", "/admin/export-subscribers"])
def test_admin_pages_require_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_wrong_password_is_rejected(client):
    login(client, "nope")
    assert client.get("/admin").status_code == 302


def test_correct_password_logs_in(client):
    login(client)
    assert client.get("/admin").status_code == 200


def test_subscribe_adds_email_once(client):
    before = count_subscribers()
    client.post("/subscribe", data={"email": "Reader@Example.com"})
    client.post("/subscribe", data={"email": "reader@example.com"})
    assert count_subscribers() == before + 1


def test_subscribe_rejects_invalid_email(client):
    before = count_subscribers()
    client.post("/subscribe", data={"email": "not-an-email"})
    assert count_subscribers() == before


def test_post_without_csrf_token_is_rejected(client):
    site.app.config.update(WTF_CSRF_ENABLED=True)
    before = count_subscribers()
    response = client.post("/subscribe", data={"email": "reader@example.com"})
    assert response.status_code == 302
    assert count_subscribers() == before


def test_search_treats_wildcards_literally(client):
    response = client.get("/search?q=%25")  # "%" would match everything if unescaped
    with sqlite3.connect(site.DB_PATH) as db:
        expected = db.execute("SELECT count(*) FROM posts WHERE instr(title || body, '%') > 0").fetchone()[0]
    assert len(set(re.findall(rb'href="/post/(\d+)"', response.data))) == expected


def test_search_highlight_escapes_html():
    assert str(site.highlight("<b>Steak</b> is done", "steak")) == "&lt;b&gt;<mark>Steak</mark>&lt;/b&gt; is done"


def test_web_url_prefers_web_copy_and_falls_back_to_original():
    with site.app.test_request_context():
        assert site.web_url("photos/hero/IMG_3386.jpeg") == "/static/web/photos/hero/IMG_3386.webp"
        assert site.web_url("photos/hero/IMG_3386.jpeg", "small") == "/static/web-sm/photos/hero/IMG_3386.webp"
        assert site.web_url("/static/does-not-exist.jpeg") == "/static/does-not-exist.jpeg"


def test_unknown_page_returns_404(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert b"didn't make the final cut" in response.data


def test_homepage_shows_selected_work_and_services(client):
    html = client.get("/").get_data(as_text=True)
    assert html.count('class="tile"') == len(site.SELECTED_WORK_IDS)
    for service in site.SERVICES:
        assert service["title"].replace("&", "&amp;") in html


def test_pretty_date():
    assert site.pretty_date("2025-09-21 20:03:21") == "September 21, 2025"
