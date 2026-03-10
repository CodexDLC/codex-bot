# 📂 Структура проекта и Автообнаружение

[⬅️ Назад к списку гайдов](best_practices.md)

Фреймворк `codex-bot` использует паттерн **Feature Discovery** (аналог `INSTALLED_APPS` в Django). Это позволяет разбивать бота на независимые модули (фичи) и подключать их простым перечислением в конфиге.

## 🛠 Пример конфигурации фич (`settings.py`)

Мы рекомендуем выносить списки установленных модулей в отдельный файл настроек.

```python
"""
Конфигурация подключаемых фич и middleware.
"""

# 1. Фичи с интерфейсом (содержат Aiogram роутеры и оркестраторы)
INSTALLED_FEATURES: list[str] = [
    "features.telegram.commands",
    "features.telegram.bot_menu",
    "features.telegram.notifications",
    "features.telegram.contacts_admin",
]

# 2. Фичи-слушатели (обрабатывают события из Redis Stream)
INSTALLED_REDIS_FEATURES: list[str] = [
    "features.redis.notifications",
    "features.redis.errors",
]

# 3. Список middleware (модули, содержащие логику обработки обновлений)
MIDDLEWARE_CLASSES: list[str] = [
    "middlewares.user_validation",
    "middlewares.throttling",
    "middlewares.security",
    "middlewares.container",
]
```

## 🏗️ Рекомендуемая структура папок

Чтобы автообнаружение работало корректно, придерживайтесь следующей структуры:

```text
src/
└── telegram_bot/
    ├── core/                # Ядро: настройки, константы
    ├── features/            # Функциональные модули
    │   ├── telegram/        # UI-фичи (handlers.py, orchestrator.py)
    │   └── redis/           # Background-фичи (handlers.py)
    ├── middlewares/         # Пользовательские мидлвари
    ├── resources/           # Локали (.ftl), шаблоны
    └── main.py              # Точка входа
```

## 🔄 Как это работает

При запуске `FeatureDiscoveryService` проходит по этим спискам и автоматически:
1. Импортирует роутеры из `handlers.py` каждой фичи.
2. Регистрирует оркестраторы в DI-контейнере.
3. Подключает обработчики Redis Stream к диспетчеру.
4. Регистрирует "мусорные состояния" для Garbage Collector.

## 💎 Преимущества подхода
1. **Модульность**: Чтобы отключить фичу, достаточно удалить её из списка.
2. **Отсутствие циклов**: Фичи не импортируют друг друга напрямую.
3. **Чистый main.py**: Вам не нужно вручную импортировать десятки роутеров и оркестраторов.

---
**Последнее обновление:** 2025-03-09
