# 🌍 Локализация и Сборка (I18n & Factory)

[⬅️ Назад к списку гайдов](best_practices.md)

Для мультиязычных ботов мы рекомендуем использовать `aiogram-i18n` с ядром `Fluent`. Чтобы поддерживать чистоту проекта, лучше разбивать переводы по фичам, а перед запуском собирать их во временную директорию.

## 🛠 Динамическая компиляция локалей

```python
import pathlib
import shutil
import tempfile
from loguru import logger as log

def compile_locales(base_path: pathlib.Path) -> str:
    """
    Собирает все .ftl файлы из подпапок языков в единую структуру.
    Например: /locales/ru/auth.ftl + /locales/ru/main.ftl -> /tmp/bot_locales/ru/messages.ftl
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

## 🛠 Фабрика бота через BotBuilder

```python
from codex_bot.engine.factory.bot_builder import BotBuilder
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore

async def build_bot(settings: BotSettings, redis_storage: Any) -> tuple[Bot, Dispatcher]:
    """Создает и конфигурирует Bot и Dispatcher."""
    builder = BotBuilder(bot_token=settings.bot_token, fsm_storage=redis_storage)

    # Сборка локалей
    locales_path = compile_locales(pathlib.Path("resources/locales"))

    bot, dp = builder.build()

    # Подключение I18n
    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path=locales_path),
        default_locale=settings.DEFAULT_LOCALE,
    )
    i18n_middleware.setup(dp)

    return bot, dp
```

## 💎 Преимущества подхода
1. **Чистота проекта**: Переводы лежат рядом с кодом фич, а не в одном огромном файле.
2. **Безопасность**: Использование временной директории ОС гарантирует отсутствие конфликтов.
3. **Гибкость**: `BotBuilder` позволяет легко расширять стандартную сборку бота.

---
**Последнее обновление:** 2025-03-09
