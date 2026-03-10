# codex-bot — agent quick reference

## Memory
`C:\Users\prime\.claude\projects\C--install-progect-codex-bot\memory\MEMORY.md`

## Project
- Package: `C:/install/progect/codex_bot/`
- Source: `C:/install/progect/lily_website/src/telegram_bot/`
- Status: все модули реализованы, идёт code review

## Dev commands
```bash
cd C:/install/progect/codex_bot
mkdocs build --strict      # проверка документации
ruff check src/            # линтинг
mypy src/                  # типы
python -c "import codex_bot; print('ok')"
```

## Key conventions
- Все DTO: `frozen=True`, мутации через `model_copy(update=...)`
- Оркестраторы: stateless singleton, `Generic[PayloadT]`
- Redis: SET NX (атомарно), не EXISTS + SET
- ImportError: проверяем `e.name == module_path` (умный Fail Fast)
- engine/ = инфраструктура "под капотом", не публичный API
