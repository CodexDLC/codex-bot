"""
UrlSignerService — Cryptographic security service for link integrity.

Provides mechanisms for generating and verifying HMAC-signed URLs,
ensuring the integrity and expiration of links used within Telegram Mini Apps.
Prevents unauthorized forgery and session hijacking via link tampering.
"""

import hashlib
import hmac
import time
from urllib.parse import quote_plus, urlencode


class UrlSignerService:
    """Service for securing Telegram Mini App URLs via HMAC-SHA256 signatures.

    This service generates tamper-proof URLs by appending a cryptographic
    signature based on a request identifier and a timestamp. It is
    essential for protecting backend endpoints from unauthorized access
    outside the intended user session.

    Args:
        secret_key: The cryptographic key used for HMAC signature generation.
    """

    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key.encode("utf-8")

    def generate_signed_url(
        self,
        base_url: str,
        request_id: str | int,
        action: str = "reply",
    ) -> str:
        """Generate a cryptographically signed URL for Telegram Mini Apps.

        Constructs a URL including a request identifier, current timestamp,
        and an HMAC-SHA256 signature calculated over the combined payload.

        Args:
            base_url: The root domain of the Mini App host.
            request_id: A unique identifier for the specific request or entity.
            action: The logical path component identifying the target action.

        Returns:
            A fully qualified URL with integrated security parameters.
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
