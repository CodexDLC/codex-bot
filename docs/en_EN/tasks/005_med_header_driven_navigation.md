# Task 005: Header-Driven Navigation (API)

**Priority:** Medium
**Status:** Planned
**Category:** Infrastructure / HTTP

---

## 🎯 Goal
Allow the backend to control the bot's navigation by sending specific metadata in HTTP response headers.

## 🛠 Problem Statement
In a Client-Server architecture, the backend (FastAPI/REST) often knows what the next screen should be. Currently, the bot has to parse the response body to decide where to go, which bloats the Orchestrator's logic.

## 🚀 Proposed Solution
1. **Metadata Extraction**: Enhance `BaseApiClient` to return not only the JSON body but also specific headers (e.g., `X-Bot-Next-Scene`, `X-Bot-Alert`).
2. **Orchestrator Integration**: Provide a way for Orchestrators to "forward" these instructions to the `Director` without manual IF/ELSE checks.
3. **Convention**: Standardize header names for common actions like `set_scene`, `show_alert`, and `clean_history`.

## ✅ Definition of Done
- `BaseApiClient._request()` optionally returns response metadata.
- A standard pattern for "Thin Client" navigation is documented.
