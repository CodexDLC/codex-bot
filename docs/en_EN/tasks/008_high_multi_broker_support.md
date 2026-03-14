# Task 008: Multi-Broker Support (RabbitMQ & Kafka)

**Priority:** High
**Status:** Planned
**Category:** Connectivity / Scalability

---

## 🎯 Goal
Extend the Event-Driven infrastructure by adding support for enterprise-grade message brokers while maintaining a unified developer-friendly API.

## 🛠 Features
1. **Unified Router**: An abstract `EventRouter` that works identically for Redis, RabbitMQ, and Kafka.
2. **RabbitMQ Adapter**: Implementation based on `aio-pika` with support for Exchanges and Queues.
3. **Kafka Adapter**: Implementation based on `aiokafka` for high-throughput streaming.
4. **Declarative Syntax**: `@rabbit_router.message("topic.event")` decorators.

---
[⬅️ Back to Roadmap](../../ru_RU/roadmap.md)
