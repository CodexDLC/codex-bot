import time

import pytest

from codex_bot.url_signer.service import UrlSignerService


@pytest.fixture
def signer():
    return UrlSignerService(secret_key="test_secret")  # pragma: allowlist secret


def test_generate_signed_url(signer):
    url = "https://example.com"
    signed_url = signer.generate_signed_url(url, request_id=123, action="test")

    assert "https://example.com/tma/test/" in signed_url
    assert "req_id=123" in signed_url
    assert "ts=" in signed_url
    assert "sig=" in signed_url


def test_verify_signed_url_success(signer):
    url = "https://example.com"
    signed_url = signer.generate_signed_url(url, request_id=123)

    # Extract params from URL
    from urllib.parse import parse_qs, urlparse

    parsed = urlparse(signed_url)
    params = parse_qs(parsed.query)

    assert (
        signer.verify_signed_url(req_id=params["req_id"][0], timestamp=params["ts"][0], signature=params["sig"][0])
        is True
    )


def test_verify_signed_url_expired(signer):
    # Signature from the past (1 hour ago)
    past_ts = str(int(time.time()) - 3600)
    is_valid = signer.verify_signed_url(req_id="123", timestamp=past_ts, signature="any", max_age=60)
    assert is_valid is False


def test_verify_signed_url_wrong_sig(signer):
    # Future timestamp
    future_ts = str(int(time.time()) + 3600)
    assert signer.verify_signed_url(req_id="123", timestamp=future_ts, signature="wrong") is False
