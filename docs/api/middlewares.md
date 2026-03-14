# engine.middlewares — Ready-to-use middleware for Aiogram

[⬅️ Back](./README.md) | [🏠 Docs Root](../README.md)

---

## ContainerMiddleware
Обязательная мидлварь, которая внедряет DI-контейнер в контекст каждого запроса.

::: codex_bot.engine.middlewares.container.ContainerMiddleware

---

## UserValidationMiddleware
Первичная проверка пользователя по БД/Кэшу. Управляет бан-листами и обновляет статус активности.

::: codex_bot.engine.middlewares.user_validation.UserValidationMiddleware

---

## ThrottlingMiddleware
Защита от спама (Rate Limit). Использует Redis для контроля частоты запросов.

::: codex_bot.engine.middlewares.throttling.ThrottlingMiddleware

---

## DirectorMiddleware
Автоматическая инициализация объекта Director для текущего запроса.

::: codex_bot.engine.middlewares.director_middleware.DirectorMiddleware

---

## DatabaseTransactionMiddleware
Автоматическое создание и фиксация транзакции SQLAlchemy для каждого запроса.

::: codex_bot.engine.middlewares.database.DatabaseTransactionMiddleware

---

## FSMContextI18nManager
Управление локализацией на основе данных FSM.

::: codex_bot.engine.middlewares.i18n.FSMContextI18nManager
