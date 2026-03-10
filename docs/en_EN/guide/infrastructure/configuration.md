# ⚙️ Configuration (Pydantic v2)

[⬅️ Back to Best Practices](../best_practices.md)

For managing settings, we recommend using **Pydantic v2**. This allows you to validate data from `.env` at startup and use dynamic properties for computed parameters.

## 🛠 Advanced Config Example

```python
import json
from loguru import logger as log
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class BotSettings(BaseSettings):
    """
    Configuration settings for the Telegram Bot.
    """
    # --- Core ---
    bot_token: str
    secret_key: str = Field(alias="SECRET_KEY")

    # --- Topics & Channels ---
    telegram_admin_channel_id: int | None = None
    telegram_topics: dict[str, int] = {}

    @field_validator("telegram_topics", mode="before")
    @classmethod
    def parse_telegram_topics(cls, v):
        """Parses a JSON string from an environment variable into a dictionary."""
        if isinstance(v, str):
            if not v.strip(): return {}
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                log.error(f"Failed to parse TELEGRAM_TOPICS: {v}")
                return {}
        return v or {}

    # --- Roles & Permissions ---
    superuser_ids: str = ""
    owner_ids: str = ""

    @property
    def superuser_ids_list(self) -> list[int]:
        return [int(x.strip()) for x in self.superuser_ids.split(",") if x.strip()]

    @property
    def roles(self) -> dict[str, list[int]]:
        """Automatic role distribution."""
        superusers = self.superuser_ids_list
        owners = [int(x.strip()) for x in self.owner_ids.split(",") if x.strip()]
        return {
            "superuser": superusers,
            "owner": list(set(owners + superusers)),
            "admin": list(set(owners + superusers)),
        }

    # --- Backend API ---
    backend_api_url_env: str = Field(default="http://localhost:8000", alias="BACKEND_API_URL")

    @property
    def api_url(self) -> str:
        """Auto-detect URL (Docker vs Local)."""
        url = self.backend_api_url_env
        if url and "localhost" not in url and "127.0.0.1" not in url:
            return url.rstrip("/")
        return "http://localhost:8000" if self.debug else "http://backend:8000"
```

## 💎 Benefits
1. **Startup Validation**: The bot won't start if there's an error in `.env`.
2. **Typing**: You always work with objects of the correct types (int, list, dict).
3. **Dynamics**: The `api_url` property automatically adapts to the environment (Docker/Local).
4. **Security**: Aliases allow you to use any names in `.env` while keeping the code clean.

---
**Last Updated:** 2025-03-09
