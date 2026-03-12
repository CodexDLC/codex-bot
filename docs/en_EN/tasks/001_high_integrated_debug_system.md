# Task 001: Integrated Debug & Education System

**Priority:** 🔴 High
**Status:** 📅 Planned
**Target Version:** v0.3.0

## 📝 Description
Move the external CLI "ID Inspector" logic inside the bot as a system-level feature. This will allow owners to quickly get Telegram IDs (User, Chat, Channel) directly from the bot interface.

Additionally, implement an "Education Mode" that provides interactive tips and documentation about the framework's architecture directly in the `/help` section.

## 🎯 Objectives
1. **Core Feature**: Create a new system feature `debug` in `src/codex_bot/features/debug/`.
2. **IDS Tool**: Implement a command/button visible only to Owners/Admins that prints current session IDs.
3. **Framework Help**: Add a configurable toggle `FRAMEWORK_HELP` in project settings.
4. **Conditional UI**: If `FRAMEWORK_HELP` is enabled, inject library-specific tutorials into the standard `/help` response.

## 🛠 Technical Notes
- Use the existing `BotContainer` to restrict access (RBAC).
- Education content should be available in both English and Russian (i18n).
- The `debug` feature should be auto-discovered just like `errors` or `bot_menu`.

## ✅ Definition of Done
- [ ] Owner can click "🔍 Inspect IDs" in the help menu.
- [ ] Bot prints User ID, Chat ID, and Thread ID.
- [ ] Toggling `FRAMEWORK_HELP` in `settings.py` hides/shows tutorial buttons.
- [ ] Documentation updated to reflect new debug capabilities.
