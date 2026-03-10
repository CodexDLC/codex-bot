# 📝 Logging (Loguru)

[⬅️ Back to Best Practices](../best_practices.md)

We recommend using the `loguru` library instead of the standard `logging`. It's easier to configure, supports file rotation out of the box, and makes logs readable.

## 🛠 Setup and Usage

```python
from loguru import logger

# 1. Setup in main.py
logger.add(
    "logs/bot.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    format="{time} {level} {message}"
)

# 2. Usage in an orchestrator
logger.info(f"User {user_id} entered feature {feature_name}")

# 3. Error logging with traceback
try:
    await some_api_call()
except Exception as e:
    logger.exception("API call failed") # Automatically adds the traceback
```

## 💎 Benefits
1. **Simplicity**: No need to manually configure handlers and formatters.
2. **Readability**: Colored console output and clear messages.
3. **Rotation**: Automatic management of log file sizes.
4. **Tracebacks**: The `logger.exception` method is a lifesaver when debugging async code.

---
**Last Updated:** 2025-03-09
