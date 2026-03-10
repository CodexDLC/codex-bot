# 🧭 Documentation Standard for codex-bot

> **AUTHORITY:** This document defines how documentation is written, structured, and maintained in the `codex-bot` library.

---

## 1. 📜 Core Philosophy

We maintain documentation in **two languages** to ensure international accessibility while keeping the local community engaged.

### 🇬🇧 English (Primary / Technical Truth)

- **Mandatory for:** All Pull Requests and technical specifications.
- **Location:**
  - `docs/api/` — Technical API reference (auto-generated from docstrings).
  - `docs/en_EN/` — Conceptual guides and architectural mirroring.
- **Content:**
  - Full technical specifications.
  - API documentation (via `docs/api/`).
  - Code examples and integration guides.
- **Goal:** Single source of truth. If code contradicts EN docs, it is a bug.

### 🇷🇺 Russian (Secondary / Conceptual Hub)

- **Optional for Contributors:** If you don't speak Russian, write EN docs. Maintainers will add RU translation.
- **Location:** `docs/ru_RU/` (mirrors folder structure).
- **Content:**
  - Conceptual translation (the "why" and "how").
  - Links to `docs/api/` for technical details instead of duplication.
  - Architect's mental model and design decision explanations.
- **Goal:** Help Russian-speaking developers understand the "why" behind the framework's architecture.

---

## 2. ☯️ Twin Realms Principle

Documentation languages serve different purposes:

### 🇬🇧 EN = Technical Truth

- **For:** AI generators, external libraries, standards compliance.
- **Format:** Granular (mirrors `src/codex_bot/` structure).
- **Contains:**
  - API Reference (in `docs/api/`).
  - Mermaid Diagrams (Sequence, Class, ER).
  - Integration patterns.

### 🇷🇺 RU = Architect's Mind

- **For:** Human developers, system understanding.
- **Format:** Aggregated (1 folder = 1 README).
- **Contains:**
  - **The Why:** Why this solution (e.g., why Stateless Orchestrators) was chosen.
  - **The Flow:** How data flows through the system (simplified).
  - **Links:** References to `docs/api/` files for technical details.

---

## 3. 🗂️ Structure Mirroring Rule

Documentation structure **MUST** mirror the code structure in `src/codex_bot/`.

### Mapping Example

| Code Location | Documentation Location (EN/RU) |
|:---|:---|
| `src/codex_bot/base/` | `docs/[lang]/architecture/base/` |
| `src/codex_bot/engine/router_builder/` | `docs/[lang]/architecture/engine/router_builder/` |
| `src/codex_bot/redis/` | `docs/[lang]/architecture/redis/` |

### Why?

- **1:1 Mapping:** Easy to find docs for any code module.
- **No Orphans:** Prevents documentation from getting lost.
- **Refactoring Safety:** When code moves, docs move with it.

---

## 4. 🧭 Navigation Standard

Every documentation file must be easily navigable.

### Breadcrumbs (Mandatory)

Every file **MUST** start with a navigation header:

```markdown
[⬅️ Back](../README.md) | [🏠 Docs Root](../../README.md)
```

- **Back:** Links to the current directory's `README.md`.
- **Docs Root:** Links to the documentation root (`docs/README.md`).

### Index Files (README.md)

Every directory **MUST** have a `README.md` acting as a navigation hub.

**Required Structure:**

1. **Header:** Emoji 📂 + Section Name.
2. **Navigation:** Breadcrumbs.
3. **Description:** Short summary (2-3 sentences).
4. **Map:** Table or list of files in **logical reading order** (not alphabetical).

---

## 5. 📝 File Naming & Organization

### Naming Conventions

- **Format:** `snake_case.md` (e.g., `orchestrator_logic.md`).
- **No Prefixes:** Do NOT use `01_`, `02_` prefixes in filenames.
- **Reading Order:** Defined in `README.md` map.

### Language Folders

All documents **MUST** reside in:

- `docs/api/` (Technical EN)
- `docs/en_EN/` (Conceptual EN)
- `docs/ru_RU/` (Conceptual RU)

---

## 6. ✅ Markdown Linting Rules (Strict)

1. **MD047 (End with Newline):** Every file must end with exactly **one newline** (`\n`).
2. **MD032 (List Spacing):** Blank line before and after any list.
3. **MD007 (Indentation):** Use **2 spaces** for nested lists.

---

## 7. 🚫 Common Mistakes

- **❌ Duplicating Code in RU Docs:** Link to `docs/api/` instead.
- **❌ Numbered Prefixes:** Use `README.md` map for order.
- **❌ Missing Breadcrumbs:** Always add the navigation header.
- **❌ Language-neutral folders:** Use `en_EN` or `ru_RU`.

---

**Last Updated:** 2025-02-07
