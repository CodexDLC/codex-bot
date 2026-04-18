"""
Abstract API Orchestrator — Persistent asynchronous HTTP client implementation.

Provides a foundational execution context for external API interactions, utilizing
long-lived connection pooling via `httpx`. Designed to minimize TLS handshake
overhead and manage multi-service request lifecycles within the DI container.
"""

import logging
from typing import Any

log = logging.getLogger(__name__)

try:
    import httpx
except ImportError as e:
    raise ImportError("BaseApiClient requires 'httpx'. Install it: pip install codex-bot[http]") from e


class ApiClientError(Exception):
    """Base HTTP client error."""


class BaseApiClient:
    """
    Base async HTTP client with a long-lived connection pool.

    Created once in the DI container, not per-request.
    Reuses TCP connections via httpx connection pooling.
    Call ``close()`` when stopping the bot for proper termination.

    Args:
        base_url: Base API URL (e.g., ``"https://api.example.com"``).
        api_key: API key for the ``X-API-Key`` header. ``None`` — no authentication.
        timeout: Total request timeout in seconds (``connect`` is always 5 sec).

    Example:
        ```python
        class BookingApiClient(BaseApiClient):
            async def get_slots(self, date: str) -> list[dict]:
                return await self._request("GET", "/slots", params={"date": date})

        # In the DI container — once:
        client = BookingApiClient(base_url="https://api.example.com", api_key="secret")

        # When stopping the bot:
        await client.close()
        ```
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            headers["X-API-Key"] = api_key

        # Long-lived client — created once, lives for the entire bot duration
        self.client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=httpx.Timeout(timeout, connect=5.0),
        )

    async def close(self) -> None:
        """Closes the connection pool. Call when stopping the bot.

        Example:
            ```python
            # In on_shutdown hook:
            await api_client.close()
            ```
        """
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Performs an HTTP request via the long-lived client.

        Args:
            method: HTTP method (``"GET"``, ``"POST"``, ``"PUT"``, ``"DELETE"``).
            endpoint: Endpoint path (e.g., ``"/api/v1/slots"``).
            json: Request body in JSON format.
            params: Query parameters.

        Returns:
            Parsed JSON response or ``None`` for 204 No Content.

        Raises:
            ApiClientError: For HTTP errors or connection issues.
        """
        url = endpoint.lstrip("/")

        try:
            log.debug(f"API {method} /{url} | params={params}")
            response = await self.client.request(method=method, url=url, json=json, params=params)
            response.raise_for_status()

            # 204 No Content and empty responses (DELETE, some POST)
            if response.status_code == 204 or not response.content:
                return None

            return response.json()

        except httpx.HTTPStatusError as e:
            log.error(f"API HTTP error {e.response.status_code}: {e.response.text}")
            raise ApiClientError(f"HTTP {e.response.status_code}") from e
        except httpx.RequestError as e:
            log.error(f"API connection error: {e}")
            raise ApiClientError(f"Connection error: {e}") from e
