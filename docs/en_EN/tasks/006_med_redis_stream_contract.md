# Task 006: Unified Envelope Contract (Redis & API)

**Priority:** Medium
**Status:** Planned
**Category:** Core / Architecture

---

## 🎯 Goal
Standardize data exchange between the bot and external systems (Redis Streams, REST API, Webhooks). Every message should be treated as an "Envelope" containing System Metadata and Business Payload.

## 🛠 Unified Structure
The system will adopt a symmetric structure for all communication channels:

### 1. Structure (JSON)
```json
{
  "meta": {
    "type": "event.type",
    "user_id": 12345,
    "__next_scene__": "target_feature",
    "trace_id": "uuid-string"
  },
  "payload": {
    "data_field_1": "value",
    "data_field_2": 42
  }
}
```

### 2. HTTP/API Mapping
For REST responses, `BaseApiClient` will be responsible for building this envelope:
- **Meta**: Extracted from custom HTTP headers (e.g., `X-Bot-*`) AND/OR a `meta` field in the JSON body.
- **Payload**: The main data from the response body.

### 3. Redis Stream Mapping
The `BotRedisDispatcher` will expect the same JSON structure in the stream message.

## 🚀 Benefits
- **Full Symmetry**: The logic for switching scenes or identifying users is identical for both background tasks and direct API calls.
- **Simplified Orchestrators**: Orchestrators receive a pre-parsed Envelope and don't need to know the origin of the data.
- **Scalability**: New system fields (like caching hints or analytics tags) can be added to `meta` without breaking feature logic.

## ✅ Definition of Done
- `EnvelopeDTO` implemented in `codex_bot.base`.
- `BaseApiClient` supports envelope assembly from headers and body.
- `BotRedisDispatcher` supports envelope-based dispatching.
