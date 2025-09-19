import pytest
import httpx

from src.fetch import Fetcher


def test_fetch_success(monkeypatch):
    """Test that Fetcher returns content on success."""

    def mock_get(url, timeout=15):
        class MockResponse:
            text = "<MPD></MPD>"

            def raise_for_status(self):
                return None

        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    content = Fetcher.get("http://example.com/test.mpd")
    assert content.strip() == "<MPD></MPD>"


def test_fetch_empty(monkeypatch):
    """Test that empty response raises ValueError."""

    def mock_get(url, timeout=15):
        class MockResponse:
            text = "   "

            def raise_for_status(self):
                return None

        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    with pytest.raises(ValueError, match="empty"):
        Fetcher.get("http://example.com/empty.mpd")


def test_fetch_http_error(monkeypatch):
    """Test that HTTP error raises ValueError."""

    def mock_get(url, timeout=15):
        raise httpx.RequestError("boom")

    monkeypatch.setattr(httpx, "get", mock_get)

    with pytest.raises(ValueError, match="Failed to fetch"):
        Fetcher.get("http://example.com/fail.mpd")
