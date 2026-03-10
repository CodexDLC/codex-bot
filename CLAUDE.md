# codex-bot — AI Context

Feature-based Aiogram framework library. MIT license, public GitHub.

---

## Agent Memory

> **Memory directory:** `C:\Users\prime\.claude\projects\C--install-progect-codex-bot\memory\`
>
> Агент из любого проекта: читай `MEMORY.md` там — это индекс.
> Детали в: `architecture.md`, `modules.md`, `fixes.md`

---

## Структура пакета

```
src/codex_bot/
├── base/               ← BaseBotOrchestrator[T] (ABC), UnifiedViewDTO, ViewResultDTO
├── director/           ← Director, OrchestratorProtocol, ContainerProtocol, SceneConfig
├── fsm/                ← BaseStateManager, GarbageStateRegistry, common_fsm_router
├── sender/             ← ViewSender (stateless), SenderManager, SenderKeys
├── redis/              ← RedisRouter, BotRedisDispatcher, RedisStreamProcessor
├── animation/          ← UIAnimationService, AnimationType
├── helper/             ← ContextHelper
├── url_signer/         ← UrlSignerService
└── engine/             ← инфраструктура "под капотом"
    ├── middlewares/    ← ThrottlingMiddleware, ContainerMiddleware, UserValidationMiddleware
    ├── discovery/      ← FeatureDiscoveryService (service.py)
    ├── factory/        ← BotBuilder (bot_builder.py)
    ├── router_builder/ ← collect_feature_routers, build_main_router (router_builder.py)
    ├── http/           ← BaseApiClient, ApiClientError (api_client.py)
    └── i18n/           ← compile_locales (locales_compiler.py)
```

---

## Стандарты (обязательно)

- **Packaging**: Hatchling, PEP 621
- **Docstrings**: Google style — Args / Returns / Example
- **Docs**: MkDocs Material + mkdocstrings
- **DTO**: `frozen=True, arbitrary_types_allowed=True`, мутации через `model_copy(update=...)`
- **Оркестраторы**: stateless `Generic[PayloadT]`, `director` явный аргумент
- **Fail Fast**: умный `except ImportError` (проверяем `e.name == module_path`)
- **Redis**: SET NX вместо EXISTS + SET (атомарно, нет race condition)
- **SecurityMiddleware**: удалён навсегда (иллюзорная защита + лишний HGETALL)
