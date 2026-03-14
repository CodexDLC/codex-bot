# Getting Started with codex-bot

This guide will walk you through the process of setting up your environment and creating your first feature using the best practices of the **codex-bot** framework.

---

## 💎 Philosophy: Universal Constructor

**codex-bot** is an evolving constructor with "batteries included." It is designed as a flexible tool that significantly accelerates the development of complex systems by offering ready-made architectural solutions for common tasks.

The framework supports a wide variety of use cases:

*   **Standalone Bot**: All business logic is implemented directly within the bot.
*   **Smart Client**: The bot acts as an interface that requests data via API and visualizes it for the user.
*   **Event Gateway**: Receiving external webhooks from your backend to instantly send notifications to channels or direct messages.
*   **Digital Assistant**: Guiding users through complex scenarios while maintaining context and state synchronization.

The true strength of **codex-bot** lies in its ability to operate within complex ecosystems (integrated with websites, workers, and APIs), serving as a reliable bridge between your backend and the user in Telegram.

---

## 🚀 Step 1: Environment Setup

For cleanliness and order, always use a virtual environment.

1. **Create your project directory**:
   ```bash
   mkdir my_project && cd my_project
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # For Windows:
   venv\Scripts\activate
   # For Linux/macOS:
   source venv/bin/activate
   ```

3. **Install the framework**:
   ```bash
   pip install codex-bot
   ```

---

## 🛠️ Step 2: Project Initialization

Run the initialization command directly **from the root of your project**. The CLI will deploy the necessary infrastructure in the current folder and isolate the bot's code in the `src/` directory.

```bash
codex-bot startproject my_bot
```

### What will happen:
- Management files will appear in the root: `pyproject.toml`, `manage.py`, `.env`.
- The bot's code skeleton will be created in the `src/my_bot/` folder.
- If you run the command in an existing project (Django, FastAPI), the CLI will offer **Smart Merge** mode.

After generation, install your new project's dependencies:
```bash
pip install -e .
```

---

## 🧩 Step 3: Creating Your First Feature

Features are independent modules of your bot. Let's create a "Profile" feature:

```bash
codex-bot create-feature profile
```

The CLI will create the `src/my_bot/features/telegram/profile/` folder with a complete structure: Handlers, Logic, and UI layers.

---

## ✍️ Step 4: Writing Logic (Best Practices)

In `logic/orchestrator.py`, we recommend using the built-in "batteries": **StateManager** and **Smart Resolver**.

```python
async def render_content(self, payload: Any, director: Director) -> ViewResultDTO:
    # 1. Isolated feature state
    fsm = ProfileStateManager(director.state)

    # 2. Smart data fetching (backend-driven navigation)
    raw_data = await director.container.api.get_profile(director.user_id)
    data = await director.resolve(raw_data)

    if isinstance(data, UnifiedViewDTO):
        return data # Redirected to another scene

    # 3. Clean UI layer
    return self.ui.render_main(data)
```

---

## 🏁 Step 5: Execution

Launch the bot using the generated management script:

```bash
python manage.py run
```

---

## 🔍 What's Next?
- Learn how the **[Director](../architecture/services/director/README.md)** manages transitions.
- Explore the **[Stateless UI](../architecture/services/view_sender/README.md)** concept in ViewSender.
- See how **[Redis Streams](../architecture/services/redis/README.md)** work for background processing.
