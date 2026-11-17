"""Tests for the /posting endpoint.

The platform calls are replaced with fake objects, so the tests
never post anything for real and never need API keys.

Run them with:  pytest
"""

from fastapi.testclient import TestClient

from app.main import app
from app.services import posting_service

client = TestClient(app)

VALID_MESSAGE = (
    "Check out our latest business platform and grow your online "
    "visibility. https://example.com"
)


class FakeOkPlatform:
    """Pretends to be a platform that always works."""

    name = "FakeOK"
    public_access = True

    def post(self, message: str) -> dict:
        return {
            "platform": self.name,
            "status": "success",
            "posted_url": "https://example.com/post/1",
            "public_access": True,
            "date": "2026-11-15",
            "time": "10:30:00",
            "error": None,
        }


class FakeBrokenPlatform:
    """Pretends to be a platform that raises an unexpected error."""

    name = "FakeBroken"
    public_access = True

    def post(self, message: str) -> dict:
        raise RuntimeError("Authentication failed")


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------
def test_valid_message_posts_and_reports_every_platform(monkeypatch):
    monkeypatch.setattr(
        posting_service,
        "get_platforms",
        lambda: [FakeOkPlatform(), FakeBrokenPlatform()],
    )

    response = client.post("/posting", json={"message": VALID_MESSAGE})

    assert response.status_code == 200
    data = response.json()

    # One platform worked -> overall success
    assert data["success"] is True
    assert len(data["results"]) == 2

    ok, broken = data["results"]
    assert ok["status"] == "success"
    assert ok["posted_url"] == "https://example.com/post/1"
    assert ok["error"] is None
    assert ok["date"] is not None
    assert ok["time"] is not None

    # A broken platform must be reported, not crash the request
    assert broken["status"] == "failed"
    assert broken["posted_url"] is None
    assert "Authentication failed" in broken["error"]


def test_success_is_false_when_every_platform_fails(monkeypatch):
    monkeypatch.setattr(
        posting_service, "get_platforms", lambda: [FakeBrokenPlatform()]
    )

    response = client.post("/posting", json={"message": VALID_MESSAGE})

    assert response.status_code == 200
    assert response.json()["success"] is False


# ---------------------------------------------------------------------------
# Validation errors (each one must give HTTP 422)
# ---------------------------------------------------------------------------
def test_message_longer_than_200_characters_is_rejected():
    response = client.post("/posting", json={"message": "x" * 201})
    assert response.status_code == 422
    assert "200 characters" in response.text


def test_message_without_a_link_is_rejected():
    response = client.post("/posting", json={"message": "Hello world, no link here"})
    assert response.status_code == 422
    assert "exactly one CTA link" in response.text


def test_message_with_two_links_is_rejected():
    message = "Visit https://a.com and also https://b.com today"
    response = client.post("/posting", json={"message": message})
    assert response.status_code == 422
    assert "exactly one CTA link" in response.text


def test_invalid_url_is_rejected():
    response = client.post("/posting", json={"message": "Check https://nodot here"})
    assert response.status_code == 422
    assert "not a valid URL" in response.text


def test_empty_message_is_rejected():
    response = client.post("/posting", json={"message": "   "})
    assert response.status_code == 422


def test_missing_message_field_is_rejected():
    response = client.post("/posting", json={})
    assert response.status_code == 422


def test_message_at_exactly_200_characters_is_accepted(monkeypatch):
    monkeypatch.setattr(posting_service, "get_platforms", lambda: [FakeOkPlatform()])

    # Build a message that is exactly 200 characters and has one link.
    link = " https://example.com"
    filler = "a" * (200 - len(link))
    message = filler + link
    assert len(message) == 200

    response = client.post("/posting", json={"message": message})
    assert response.status_code == 200
    assert response.json()["success"] is True
