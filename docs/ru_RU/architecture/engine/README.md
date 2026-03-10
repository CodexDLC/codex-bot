# ⚙️ Engine

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

Модуль `engine` предоставляет основную инфраструктуру для сборки и запуска `aiogram` бота с использованием `codex-bot`.

---

## 🧠 Почему так?

### Параметрическая сборка (Parametric Assembly)
В большом боте главный роутер и диспетчер могут стать перегруженными импортами. Модуль `engine` решает это через **Параметрическую сборку** (через `RouterBuilder` и `BotBuilder`). Это позволяет явно контролировать порядок мидлварей и фич без хардкода в одном файле.

### Автообнаружение фич (Feature Discovery)
`FeatureDiscoveryService` автоматизирует регистрацию фич (роутеров, оркестраторов, конфигов меню и мусорных состояний). Это следует паттерну **Django INSTALLED_APPS**, позволяя легко добавлять или удалять фичи простым обновлением списка в настройках.

---

## 🔄 Поток данных (The Flow)

1. **Обнаружение:** `FeatureDiscoveryService` сканирует список `installed_features` и импортирует их `handlers.py` и `feature_setting.py`.
2. **Сборка:** `RouterBuilder` собирает все объекты `Router` из обнаруженных фич и включает их в главный роутер.
3. **Конфигурация:** `BotBuilder` создает экземпляры `Bot` и `Dispatcher`, инжектируя обнаруженные фичи и мидлвари в заданном порядке.
4. **Запуск:** Бот начинает поллинг, со всеми фичами и инфраструктурой (i18n, throttling, container), готовыми к обработке запросов.

---

## 🗺️ Карта модуля

| Компонент | Описание |
|:---|:---|
| **[📄 Router Builder](../../../api/router_builder.md)** | `build_main_router` и `collect_feature_routers`. |
| **[📄 Discovery](../../../api/discovery.md)** | `FeatureDiscoveryService` для автообнаружения и регистрации. |
| **[📄 Factory](../../../api/factory.md)** | `BotBuilder` для создания `Bot` и `Dispatcher`. |
| **[📄 Middlewares](../../../api/middlewares.md)** | `UserValidation`, `Throttling`, `Container` и `I18n` мидлвари. |
| **[📄 HTTP Client](../../../api/http.md)** | `BaseApiClient` с пулом соединений. |
| **[📄 I18n Compiler](../../../api/i18n.md)** | `compile_locales` для Fluent (.ftl) файлов. |

---

**Последнее обновление:** 2025-02-07
