# Architecture Overview

The **codex-bot** architecture is built on the principles of loose coupling and high modularity. We divide the system into three primary layers: **Engine**, **Services**, and **Features**.

---

## 🏗 Three System Layers

### 1. Engine
The foundation of the framework. It handles the bot's lifecycle, automated assembly, and infrastructure.
*   **[Discovery](./engine/discovery.md)**: Automated feature search and registration.
*   **[BotBuilder](./engine/factory.md)**: Assembler for Bot and Dispatcher objects.
*   **[Container](./engine/container.md)**: DI container for storing all system objects.

### 2. Core Services
A set of tools you use to implement bot logic.
*   **[Director](./services/director/README.md)**: The coordinator service that manages transitions between features.
*   **[ViewSender](./services/view_sender/README.md)**: Responsible for UI delivery and message synchronization.
*   **[Base Orchestrator](./services/base/README.md)**: The base class for implementing business logic.
*   **[FSM & States](./services/fsm/README.md)**: State management system with data isolation.

### 3. Business Features (Features)
Your application code. Each feature is a directory containing:
*   **handlers/**: Telegram event handlers.
*   **logic/**: Orchestrator and state managers.
*   **ui/**: Interface descriptions (texts and buttons).
*   **feature_setting.py**: Configuration and feature entry point.

---

## 🔄 Request Processing Flow

1. Telegram sends an event (Message/Callback).
2. **Middlewares** prepare the context and create a **Director** object.
3. The **Director** finds the required **Orchestrator** and passes control to it.
4. The **Orchestrator** executes the logic and returns a `UnifiedViewDTO`.
5. The **ViewSender** delivers the result to the user by updating existing messages.

---

## 🧭 What to Study Next?
- See how **[Smart Navigation](./services/director/README.md)** works via the Director.
- Learn about **[FSM Isolation](./services/fsm/README.md)** to prevent data conflicts.
