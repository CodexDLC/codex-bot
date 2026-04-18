# Codex Bot Documentation Standard

## 1. 📂 Domain-Driven Structure
We divide documentation not by code files, but by **Purpose (Domain/Service)**. This structure ensures readiness for monorepo expansion or separate library extraction.

| Section (EN/RU) | Description | Content (examples) |
| :--- | :--- | :--- |
| architecture/domains/ | Core Business Logic | booking, calculator, calendar |
| architecture/services/ | Infrastructure Services | llm, notifications, worker, redis |
| architecture/platform/ | Base Utils & Configs | common, core, settings, schemas |
| architecture/adapters/ | Framework Bridges | django, arq |

---

## 2. 🛠 API Reference (docs/api/) — Code Mirror
Markdown files in this section mirror the Python module structure in `src/`.

- **Hierarchy:** If the code is at `src/codex_bot/fsm/state_manager.py`, the API doc should be at `docs/api/fsm/state_manager.md`.
- **Grouping:** In the MkDocs menu: `API Reference -> fsm -> state_manager`.
- **Content:** Each file uses the `::: codex_bot.module_name` directive to automatically extract classes and functions from docstrings.

---

## 3. 🗺 Architecture Guides — Logic Mirror
These guides describe the **Domain as a whole** to provide a high-level overview of interactions.

Inside `architecture/domains/` (or `services/`):
- **Domain Folder:** Create a subfolder for each major node (e.g., `architecture/domains/booking/`).
- **Files inside:**
    - `README.md` — Entry point: general diagram, domain purpose, quick start.
    - `logic_deep_dive.md` — (Optional) Detailed description of complex algorithms (e.g., `ChainFinder`).
    - `data_flow.md` — Data flow diagram (from DTO to response).

---

## 4. 🧭 Content Mapping Example

| Content Type | Code Path | Docs Path (EN/RU) | Writing Style |
| :--- | :--- | :--- | :--- |
| **API** | `fsm/state_manager.py` | `docs/api/fsm/state_manager.md` | Reference: fields, types, validation. |
| **API** | `base/view_dto.py` | `docs/api/base/view_dto.md` | Reference: DTO structure and immutability rules. |
| **Architecture** | `fsm/` | `docs/[lang]/architecture/services/fsm/README.md` | Guide: How to use state isolation and GC. |

---

## 5. 🚀 Evolution (Roadmap & Tasks)
The `docs/evolution/` folder is used for project development management. It is identical in both RU and EN versions.

- **Roadmap:** `docs/evolution/roadmap.md` — Global development plan.
- **Tasks:** `docs/evolution/tasks/[domain_name]/[task_name].md` — Specific feature tasks.
- **Architecture Links:** Every task must reference the API or Architecture guide it affects.

---

## 6. 🛠 Development Standards (Code Quality)

- **Zero Any:** Using `Any` is strictly prohibited. Use `Protocol`, `TypeVar`, or `Generic` for unknown types.
- **Strict Protocols:** Always use `@runtime_checkable` protocols for Dependency Inversion.
- **Google-style Docstrings:** Every class and public method MUST have docstrings with `Args`, `Returns`, `Raises`, and `Example` blocks.
- **Stateless Core:** Services and Orchestrators must not store user state in `self`. Use the `Director` context.
- **I18n Namespacing:** All Fluent keys (`.ftl`) MUST start with the feature prefix (e.g., `auth-login-btn`) to prevent collisions during automated merging.

---

## 7. ☯️ Strict Mirroring Rule
The `ru_RU` and `en_EN` folders must be structurally identical.
If a new diagram is added to `docs/en_EN/architecture/domains/booking.md`, it **must** appear in the corresponding RU file.

---

## 8. 🧭 Navigation Standard (Breadcrumbs)
Every file must start with breadcrumbs for easy navigation:

```markdown
[⬅️ Back to Section](../README.md) | [🗺 Roadmap](../../evolution/roadmap.md) | [🏠 Home](../../../README.md)
```
