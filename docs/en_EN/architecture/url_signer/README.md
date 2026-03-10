# 🔗 URL Signer

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `url_signer` module provides a service for generating and verifying HMAC-signed URLs for Telegram Mini Apps in the `codex-bot` framework.

---

## 🧠 The Why

### Security (Forgery Protection)
When a bot sends a link to a Telegram Mini App (TMA), it often needs to pass sensitive data (e.g., `request_id`, `user_id`) in the URL. Without a signature, a user could manually modify these parameters to access unauthorized data. `UrlSignerService` uses **HMAC-SHA256** to sign the URL, ensuring that any modification will invalidate the signature.

### Expiration (Time-Limited Links)
Some links should only be valid for a short period (e.g., 5 minutes). `UrlSignerService` includes a **timestamp** in the signature, allowing you to set a maximum age for the link. This reduces the risk of old links being reused.

---

## 🔄 The Flow

1. **Generation:** The bot calls `signer.generate_signed_url(base_url, request_id, action)`.
2. **Signing:** The service creates a payload string (`request_id:timestamp`) and signs it with a secret key using HMAC-SHA256.
3. **URL Building:** The signature and timestamp are added as query parameters to the URL.
4. **Verification:** When the Mini App receives the request, it calls `signer.verify_signed_url(req_id, ts, sig)`.
5. **Validation:** The service re-calculates the signature and checks if the timestamp is within the `max_age` limit.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/url_signer.md)** | Technical details for `UrlSignerService`. |
| **[📄 URL Signer Service](../../../api/url_signer.md#urlsignerservice)** | HMAC-signed URLs for Mini Apps. |

---

**Last Updated:** 2025-02-07
