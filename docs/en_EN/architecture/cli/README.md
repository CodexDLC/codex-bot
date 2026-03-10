# 🛠️ CLI

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `cli` module provides a command-line interface for rapid feature development and project scaffolding in the `codex-bot` framework.

---

## 🧠 The Why

### Standardized Scaffolding
In a feature-based architecture, every module must follow a strict directory structure (handlers, logic, ui, resources, etc.). Manually creating these folders and files is error-prone and tedious. The `codex-bot` CLI automates this process, ensuring that every new feature is consistent with the framework's standards from the start.

### Rapid Prototyping
By using pre-defined templates, developers can generate a fully functional "Hello World" feature (including FSM states, keyboards, and orchestrators) in seconds. This allows for faster iteration and prototyping of new bot capabilities.

---

## 🔄 The Flow

1. **Command:** The developer runs `codex-bot create-feature <name> [--type redis]`.
2. **Template Loading:** The CLI loads the appropriate `.py.tpl` files from the library's internal `templates` directory.
3. **Variable Injection:** The CLI injects the feature name, class names, and keys into the templates.
4. **File Creation:** A new directory structure is created in the project's `features/` folder, populated with the generated files.
5. **Integration:** The developer is prompted to add the new feature path to the `INSTALLED_FEATURES` list in their settings.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/cli.md)** | Technical details for CLI commands. |
| **[📄 create-feature](../../../api/cli.md#create-feature)** | Scaffolding command for new features. |

---

**Last Updated:** 2025-02-07
