# UI Animation Service

The `UIAnimationService` is designed to provide visual feedback ("waiting") within the Telegram UI. It allows you to show users progress bars or infinite loading indicators while the bot performs a long-running background task.

---

## 🛠 Why is it needed?

In Telegram, bot interaction should feel instantaneous. If an operation (e.g., searching for an opponent or requesting a heavy API) takes more than 1-2 seconds, the user might think the bot has frozen.

`UIAnimationService` solves this problem by transforming a static message into a dynamic interface with animation.

---

## 🚀 Key Scenarios

The service supports three behavioral models:

### 1. Delayed Fetch (`run_delayed_fetch`)
Animation is shown for a fixed time first, and only at the end is the request for data executed.
- **Application**: Simulated searching, data "scanning" where you want to create the effect of the system working.
- **Animation Type**: Usually `PROGRESS_BAR`.

### 2. Polling Loop (`run_polling_loop`)
The bot makes requests to the backend/database every N seconds. While the status is `is_waiting=True`, a running indicator cycles in the message.
- **Application**: Waiting for transaction confirmation, arena player matching, waiting for an LLM response.
- **Animation Type**: Usually `INFINITE` (running indicator).

### 3. Timed Polling (`run_timed_polling`)
A combined mode. A progress bar is shown based on an expected time (e.g., 10 seconds for movement), but the bot simultaneously continues to check the real status.
- **Application**: Movement timers in RPGs, long calculations with a known completion time.

---

## ✍️ How to Use

The service is typically initialized in the container and accessed via `container.animation_service`.

### Example in an Orchestrator:

```python
async def handle_action(self, payload, director: Director):
    animation = director.container.animation_service

    async def check_status():
        # Real status check logic
        res = await api.get_job_status(payload.job_id)
        return build_view(res), res.is_pending

    # Start the polling loop
    await animation.run_polling_loop(
        check_func=check_status,
        loading_text="⏳ <b>Processing data...</b>",
        animation_type=AnimationType.INFINITE
    )
```

### Controlling Animation Placement
You can specify the `{ANIMATION}` placeholder in the orchestrator's text. The service will insert the indicator exactly there. If no placeholder is present, the animation will be appended to the end of the message.

```python
# In ViewResultDTO
text = "Task Status: {ANIMATION}\nPlease do not close the menu."
```

---

## 📊 Animation Types (`AnimationType`)

1. **`PROGRESS_BAR`**: Filling bar `[■■■□□□□□□□] 30%`.
2. **`INFINITE`**: Running block `[□□■□□□□□□□]`.
3. **`NONE`**: Just text without a graphical indicator.

---

## 🧭 Related Components
- **[ViewSender](../view_sender/README.md)** — used for sending animation frames to the user.
- **[Director](../../README.md)** — provides access to the service via the container.
