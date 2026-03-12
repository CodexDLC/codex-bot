# Task 003: In-Bot Documentation Navigator (Guide System)

**Priority:** 🔴 High
**Status:** 📅 Planned
**Target Version:** v0.3.0

## 📝 Description
Implement a structured navigation system for displaying documentation directly within the Telegram bot. The system will use a hybrid approach: concise, actionable info inside the bot and a bridge to the full web documentation.

## 🎯 Objectives
1. **MVP - Quick Guide**: A system-level feature `guide` that renders core framework concepts in short, easy-to-read messages.
2. **Navigation Pattern**:
   - **Main Menu**: List of key topics (Architecture, DB, Redis, etc.).
   - **Action Buttons**: Navigation between topics.
3. **Web Bridge**: A persistent "🌐 View Detailed Documentation" button at the bottom of guide messages that links to the official website.
4. **Plug-and-Play**: Allow features to register their own "quick help" snippets.

## 🚀 Phased Implementation
- **Step 1**: Create the basic `guide` orchestrator and UI with static short texts.
- **Step 2**: Implement the "Website" button using `URL` buttons in the keyboard.
- **Step 3**: Integrate with `DiscoveryService` to allow dynamic page registration.

## 🛠 Technical Notes
- Use the `DiscoveryService` to manage the list of available guide sections.
- The website URL should be configurable via `BotSettings` (defaulting to the official docs site).

## ✅ Definition of Done
- [ ] User can see a categorized list of help topics.
- [ ] Each topic displays a concise summary.
- [ ] Every guide page has a functional link to the external documentation site.
- [ ] Navigation feels snappy and doesn't clutter the chat history (via `ViewSender`).
