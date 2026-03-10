# ⚙️ Конфигурация (Pydantic v2)

[⬅️ Назад к списку гайдов](best_practices.md)

Для управления настройками мы рекомендуем использовать **Pydantic v2**. Это позволяет валидировать данные из `.env` при запуске и использовать динамические свойства для вычисляемых параметров.

## 🛠 Пример продвинутого конфига

```python
import json
from loguru import logger as log
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class BotSettings(BaseSettings):
    """
    Настройки конфигурации для Telegram-бота.
    """
    # --- Основное ---
    bot_token: str
    secret_key: str = Field(alias="SECRET_KEY")

    # --- Топики и Каналы ---
    telegram_admin_channel_id: int | None = None
    telegram_topics: dict[str, int] = {}

    @field_validator("telegram_topics", mode="before")
    @classmethod
    def parse_telegram_topics(cls, v):
        """Парсит JSON-строку из переменной окружения в словарь."""
        if isinstance(v, str):
            if not v.strip(): return {}
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                log.error(f"Ошибка парсинга TELEGRAM_TOPICS: {v}")
                return {}
        return v or {}

    # --- Роли и Права ---
    superuser_ids: str = ""
    owner_ids: str = ""

    @property
    def superuser_ids_list(self) -> list[int]:
        return [int(x.strip()) for x in self.superuser_ids.split(",") if x.strip()]

    @property
    def roles(self) -> dict[str, list[int]]:
        """Автоматическое распределение ролей."""
        superusers = self.superuser_ids_list
        owners = [int(x.strip()) for x in self.owner_ids.split(",") if x.strip()]
        return {
            "superuser": superusers,
            "owner": list(set(owners + superusers)),
            "admin": list(set(owners + superusers)),
        }

    # --- Бэкенд API ---
    backend_api_url_env: str = Field(default="http://localhost:8000", alias="BACKEND_API_URL")

    @property
    def api_url(self) -> str:
        """Авто-детект URL (Docker vs Local)."""
        url = self.backend_api_url_env
        if url and "localhost" not in url and "127.0.0.1" not in url:
            return url.rstrip("/")
        return "http://localhost:8000" if self.debug else "http://backend:8000"
```

## 💎 Преимущества подхода
1. **Валидация на старте**: Бот не запустится, если в `.env` ошибка.
2. **Типизация**: Вы всегда работаете с объектами нужных типов (int, list, dict).
3. **Динамика**: Свойство `api_url` само адаптируется под окружение (Docker/Local).
4. **Безопасность**: Алиасы позволяют использовать любые имена в `.env`, сохраняя чистоту кода.

---
**Последнее обновление:** 2025-03-09
