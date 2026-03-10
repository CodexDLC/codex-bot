"""
UrlSignerService — Generation of HMAC-signed URLs for Telegram Mini Apps.

Provides protection against link forgery with a limited lifetime.
"""

import hashlib
import hmac
import time
from urllib.parse import quote_plus, urlencode


class UrlSignerService:
    """Generation of HMAC-signed URLs for Telegram Mini Apps.

    Signs URLs using HMAC-SHA256 and a timestamp.
    This protects against forgery and limits the link's lifetime.

    Args:
        secret_key: Secret key for signing (string).

    Example:
        ```python
        signer = UrlSignerService(secret_key=settings.secret_key)
        url = signer.generate_signed_url(
            base_url="https://myapp.example.com",
            request_id=42,
            action="reply",
        )
        # https://myapp.example.com/tma/reply/?req_id=42&ts=...&sig=...
        ```
    """

    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key.encode("utf-8")

    def generate_signed_url(
        self,
        base_url: str,
        request_id: str | int,
        action: str = "reply",
    ) -> str:
        """Generates a signed URL for a WebApp.

        Builds a URL of the form:
        ``{base_url}/tma/{action}/?req_id=...&ts=...&sig=...``

        The signature is calculated based on the string ``"{request_id}:{timestamp}"``.

        Args:
            base_url: Root URL of the site (e.g., ``"https://myapp.example.com"``).
            request_id: Request ID included in the signature.
            action: Action path (default is ``"reply"``).

        Returns:
            Full URL with signature parameters.

        Example:
            ```python
            url = signer.generate_signed_url(
                base_url="https://myapp.example.com",
                request_id=123,
                action="confirm",
            )
            ```
        """
        timestamp = str(int(time.time()))
        req_id_str = str(request_id)

        payload = f"{req_id_str}:{timestamp}".encode()
        signature = hmac.new(self._secret_key, payload, hashlib.sha256).hexdigest()

        params = {"req_id": req_id_str, "ts": timestamp, "sig": signature}
        clean_base_url = base_url.rstrip("/")

        return f"{clean_base_url}/tma/{action}/?{urlencode(params, quote_via=quote_plus)}"

    def verify_signed_url(
        self,
        req_id: str,
        timestamp: str,
        signature: str,
        max_age: int = 300,
    ) -> bool:
        """Verifies the URL signature.

        Args:
            req_id: Request ID from the ``req_id`` parameter.
            timestamp: Timestamp from the ``ts`` parameter.
            signature: Signature from the ``sig`` parameter.
            max_age: Maximum signature age in seconds (default is 300).

        Returns:
            ``True`` if the signature is valid and has not expired.

        Example:
            ```python
            is_valid = signer.verify_signed_url(
                req_id=request.query_params["req_id"],
                timestamp=request.query_params["ts"],
                signature=request.query_params["sig"],
            )
            ```
        """
        try:
            ts_int = int(timestamp)
        except ValueError:
            return False

        if int(time.time()) - ts_int > max_age:
            return False

        payload = f"{req_id}:{timestamp}".encode()
        expected = hmac.new(self._secret_key, payload, hashlib.sha256).hexdigest()

        return hmac.compare_digest(expected, signature)
