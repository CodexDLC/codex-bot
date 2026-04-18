# Development Backlog 📋

This page provides a high-level overview of planned enhancements and features.
Detailed technical requirements for active tasks are linked below.

## 🏗 Core Orchestration & Logic
- [x] **Smart Resolver**: Metadata-driven navigation logic. (See [ARCHIVE.md](./ARCHIVE.md))
- [ ] **Redis Stream FSM Integration**: Automatic context injection. [**(Task #004b)**](./004_high_redis_fsm_integration.md)
- [ ] **Unified Envelope Contract**: Standardized data exchange. [**(Task #006)**](./006_med_redis_stream_contract.md)

## 🔌 Connectivity & Integration
- [ ] **Multi-Broker Support**: RabbitMQ & Kafka adapters. [**(Task #008)**](./008_high_multi_broker_support.md)
- [ ] **Integrated Webhook Server**: Pre-configured HTTP server. [**(Task #009)**](./009_high_webhook_server.md)
- [ ] **Header-Driven Navigation**: API-controlled transitions. [**(Task #005)**](./005_med_header_driven_navigation.md)

## 🗄 Persistence & Infrastructure
- [ ] **SQLAlchemy Sender Storage**: Persistent UI coordinates. [**(Task #007)**](./007_med_sqlalchemy_sender_storage.md)
- [ ] **Docker Templates**: Generation of `docker-compose.yml` and `Dockerfile` for deployment. [**(Task #002)**](./002_med_docker_infrastructure.md)

## 🛠 Developer Experience (DX)
- [ ] **Integrated Debug System**: Visual trace and event inspector. [**(Task #001)**](./001_high_integrated_debug_system.md)
- [ ] **In-Bot Guide System**: Interactive documentation navigator. [**(Task #003)**](./003_high_in_bot_guide_system.md)

---
[⬅️ Back to Roadmap](../roadmap.md)
