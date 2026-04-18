# Project Roadmap 🗺️

The development path of **codex-bot** from a base framework to a complete Telegram development ecosystem.

---

## ✅ Phase 1: Foundation (v0.1.0) — COMPLETED
- [x] Core framework: Director, Orchestrator, ViewSender.
- [x] Discovery Engine: Automated feature search.
- [x] Basic Redis Integration: FSM and Storage.
- [x] CLI: `startproject` command and base templates.

## 🏗️ Phase 2: Protocols & Standardization (v0.2.0) — CURRENT
- [x] **Smart Merge**: Safe integration into existing projects via CLI.
- [x] **FSM Isolation**: Namespacing feature data (BaseStateManager).
- [x] **Smart Resolver**: `director.resolve()` pattern for navigation control.
- [x] **ID Inspector**: Built-in identifier debug helper.
- [ ] **Unified Envelope**: Implementation of a unified message contract. [**(Task #006)**](./tasks/006_med_redis_stream_contract.md)
- [x] **Metadata-Driven Navigation**: Full support for `__next_scene__`. [**(Backlog)**](./tasks/backlog.md)
- [ ] **Redis Stream FSM Integration**: Automatic Director injection in Redis handlers. [**(Task #004b)**](./tasks/004_high_redis_fsm_integration.md)

## 🧩 Phase 3: DX & Tooling (v0.3.0) — PLANNED
- [ ] **In-Bot Guide System**: Interactive documentation navigator. [**(Task #003)**](./tasks/003_high_in_bot_guide_system.md)
- [ ] **Status Commands**: Built-in system health diagnostics (DB, Redis, API).
- [ ] **Strict Typing**: Transition to Enums for states and transitions.
- [ ] **Contextual Hints**: Educational mode in CLI during feature creation.

## 🚀 Phase 4: Scaling & Infrastructure (v0.4.0) — PLANNED
- [ ] **Webhooks Service**: Native support for incoming webhooks (FastAPI/Aiohttp). [**(Task #009)**](./tasks/009_high_webhook_server.md)
- [ ] **Docker Infrastructure**: Ready-to-use containerization templates. [**(Task #002)**](./tasks/002_med_docker_infrastructure.md)
- [ ] **Smart Recovery**: Automated retry logic for API and DB.
- [ ] **Animation Engine**: Expanding the library of visual waiting effects.
- [ ] **SQLAlchemy Sender Storage**: Persistent UI coordinate storage without Redis. [**(Task #007)**](./tasks/007_med_sqlalchemy_sender_storage.md)

## 📡 Phase 5: Event-Driven Ecosystem (v0.5.0+) — PLANNED
- [ ] **Multi-Broker Support**: Adapters for RabbitMQ and Kafka with unified router syntax. [**(Task #008)**](./tasks/008_high_multi_broker_support.md)
- [ ] **Remote FSM Management**: User state management via brokers without Aiogram involvement.
- [ ] **Smart Routing**: Automated message distribution between multiple bot instances.

## 🧪 Testing & Quality Assurance
- [ ] **Infrastructure Coverage (High Priority)**
    - [x] Redis Routing & Dispatching Tests
    - [ ] `RedisStreamProcessor` integration tests (mock Redis).
    - [ ] CLI Automation tests (Scaffolding, Feature generation).
    - [ ] Database Repository & Migration handlers tests.
- [ ] **Feature Verification**
    - [ ] `features/errors` pipeline verification.
    - [ ] I18n Fluent compiler edge cases.

---

## 📈 Future
- **Telegram Business** integration (managing personal accounts via bots).
- Visual scenario designer plugin (No-code bridge).
