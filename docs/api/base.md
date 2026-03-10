# base — DTOs and BaseBotOrchestrator

Base immutable objects and abstract feature orchestrator.

## View DTOs

All DTOs are frozen (`frozen=True`). To modify, use `.model_copy(update={...})`.

::: codex_bot.base.view_dto.ViewResultDTO

::: codex_bot.base.view_dto.UnifiedViewDTO

::: codex_bot.base.view_dto.MessageCoordsDTO

## Context DTO

::: codex_bot.base.context_dto.BaseBotContext

## BaseBotOrchestrator

::: codex_bot.base.base_orchestrator.BaseBotOrchestrator
