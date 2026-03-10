# ✨ Animation

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `animation` module provides a waiting animation service for the Telegram UI in the `codex-bot` framework.

---

## 🧠 The Why

### User Experience (UX)
In a bot, some actions (e.g., searching, scanning, moving) can take several seconds to complete. Without feedback, users might think the bot is broken. `UIAnimationService` provides visual feedback (Progress Bars, Infinite Indicators) to keep the user engaged during long-running operations.

### Dynamic Injection
The animation service is designed to be **non-intrusive**. It can inject an animation string into an existing `UnifiedViewDTO` using a placeholder (`{ANIMATION}`). This allows you to add animations to any feature without modifying its core rendering logic.

---

## 🔄 The Flow

1. **Scenario Selection:** The developer chooses an animation scenario: `run_delayed_fetch`, `run_polling_loop`, or `run_timed_polling`.
2. **Polling:** The service calls a `PollerFunc` to check the current status of the background operation.
3. **Generation:** An ASCII animation frame (e.g., `[■■□□□] 40%`) is generated based on the current progress.
4. **Injection:** The animation string is injected into the `UnifiedViewDTO`'s text.
5. **Update:** The `ViewSender` edits the persistent UI message with the new frame.
6. **Completion:** Once the operation is finished, the final result is displayed, and the animation stops.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/animation.md)** | Technical details for `UIAnimationService`. |
| **[📄 Animation Type](../../../api/animation.md#animationtype)** | `PROGRESS_BAR`, `INFINITE`, and `NONE`. |

---

**Last Updated:** 2025-02-07
