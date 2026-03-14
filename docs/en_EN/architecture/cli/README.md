# CLI — Scaffolding and Management Engine

The CLI (Command Line Interface) in **codex-bot** is a powerful automation tool that accompanies your project at every stage: from initial setup to adding new capabilities. It ensures your project always adheres to the framework's architectural standards.

---

## 💎 CLI Philosophy

The main goal of the CLI is to eliminate routine file and directory creation ("boilerplate"). We follow three core principles:
1. **Professional Start**: Projects are immediately ready for DB, Redis, and i18n integration.
2. **Isolation**: Each feature is created in its own directory with all necessary layers (Logic, UI, Handlers).
3. **Safe Integration**: The CLI respects your existing code and avoids overwriting critical project files.

---

## 🏗 Core Commands

| Command | Purpose | Key Features |
| :--- | :--- | :--- |
| **`startproject`** | Initialize a new bot | Interactive wizard, stack configuration, Smart Merge mode. |
| **`create-feature`** | Add a business module | **Interactive mode**: helps you choose the type (Telegram/Redis) and name. |
| **`inspect`** | Debugging tool | Verify tokens and retrieve bot information directly via API. |

---

## 🚀 Interactivity and Flexibility

Generation commands (`startproject` and `create-feature`) support two modes of operation:

1. **Interactive (Wizard)**: Simply run the command without arguments. The CLI will ask necessary questions, offer choices, and validate your input.
2. **Command-line (Arguments)**: For power users or automation scripts, all parameters can be passed via flags (e.g., `--name my_feature --type redis`). In this case, no questions will be asked.

---

## 🎨 Smart Merge Mode

If you run `codex-bot startproject` in a directory that already contains a project (e.g., Django or FastAPI), the CLI enters **Smart Merge** mode:
- Configuration files (`pyproject.toml`, `manage.py`, `.env`) are created with a `.bot` suffix.
- Your bot package is isolated within the `src/{bot_name}` directory.

---

## 🧭 Related Sections
- **[Getting Started](../../guide/getting_started.md)** — Practical CLI usage.
- **[Discovery](../engine/discovery.md)** — How the engine finds what the CLI creates.
