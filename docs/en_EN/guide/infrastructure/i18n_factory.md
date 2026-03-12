# 🌍 Localization and Factory (I18n & Factory)

[⬅️ Back to Best Practices](../best_practices.md)

For multi-language bots, we recommend using `aiogram-i18n` with the `Fluent` core. To keep the project clean, it's best to split translations by feature and collect them into a temporary directory before startup.

## 🛠 Dynamic Locale Compilation

```python
import pathlib
import shutil
import tempfile
from loguru import logger as log

def compile_locales(base_path: pathlib.Path) -> str:
    """
    Collects all .ftl files from language subfolders into a single structure.
    Example: /locales/ru/auth.ftl + /locales/ru/main.ftl -> /tmp/bot_locales/ru/messages.ftl
    """
    tmp_dir = pathlib.Path(tempfile.gettempdir()) / "bot_locales"
    if tmp_dir.exists(): shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for lang_dir in base_path.iterdir():
        if not lang_dir.is_dir(): continue

        lang = lang_dir.name
        compiled_content = [f.read_text(encoding="utf-8") for f in lang_dir.glob("*.ftl")]

        if compiled_content:
            lang_tmp_dir = tmp_dir / lang
            lang_tmp_dir.mkdir(exist_ok=True)
            (lang_tmp_dir / "messages.ftl").write_text("\n".join(compiled_content), encoding="utf-8")
            log.debug(f"LocalesCompiler | Compiled {lang}")

    return str(tmp_dir / "{locale}")
```

## 🛠 Bot Factory via BotBuilder

```python
from codex_bot.engine.factory.bot_builder import BotBuilder
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore

async def build_bot(settings: BotSettings, redis_storage: Any) -> tuple[Bot, Dispatcher]:
    """Creates and configures Bot and Dispatcher."""
    builder = BotBuilder(bot_token=settings.bot_token, fsm_storage=redis_storage)

    # Compile locales
    locales_path = compile_locales(pathlib.Path("resources/locales"))

    bot, dp = builder.build()

    # Connect I18n
    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path=locales_path),
        default_locale=settings.DEFAULT_LOCALE,
    )
    i18n_middleware.setup(dp)

    return bot, dp
```

## 💎 Benefits
1. **Project Cleanliness**: Translations reside next to feature code, not in one giant file.
2. **Safety**: Using the OS temporary directory ensures no file conflicts.
3. **Flexibility**: `BotBuilder` allows easy extension of the standard bot assembly.

---
**Last Updated:** 2025-03-09
