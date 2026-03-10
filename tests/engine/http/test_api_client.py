from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_bot.engine.http.api_client import ApiClientError, BaseApiClient


@pytest.fixture
def api_client():
    return BaseApiClient(base_url="https://api.example.com/", api_key="test_key")  # pragma: allowlist secret


@pytest.mark.asyncio
async def test_api_client_request_success(api_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "ok"}

    api_client.client.request = AsyncMock(return_value=mock_response)

    result = await api_client._request("GET", "/test")

    assert result == {"data": "ok"}
    api_client.client.request.assert_called_once()


@pytest.mark.asyncio
async def test_api_client_no_content(api_client):
    mock_response = MagicMock()
    mock_response.status_code = 204

    api_client.client.request = AsyncMock(return_value=mock_response)

    result = await api_client._request("GET", "/test")
    assert result is None


@pytest.mark.asyncio
async def test_api_client_http_error(api_client):
    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    # Mock raise_for_status to raise HTTPStatusError
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Client Error", request=MagicMock(), response=mock_response
    )

    api_client.client.request = AsyncMock(return_value=mock_response)

    with pytest.raises(ApiClientError, match="HTTP 404"):
        await api_client._request("GET", "/test")


@pytest.mark.asyncio
async def test_api_client_close(api_client):
    api_client.client.aclose = AsyncMock()
    await api_client.close()
    api_client.client.aclose.assert_called_once()
