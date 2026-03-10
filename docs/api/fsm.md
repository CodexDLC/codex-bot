# fsm — FSM Manager and Garbage Collector

## BaseStateManager

::: codex_bot.fsm.state_manager.BaseStateManager

## GarbageStateRegistry

::: codex_bot.fsm.garbage_collector.GarbageStateRegistry

## IsGarbageStateFilter

::: codex_bot.fsm.garbage_collector.IsGarbageStateFilter

## common_fsm_router

A ready-to-use router with a garbage-collector handler. Connect it to the main dispatcher:

```python
from codex_bot.fsm import common_fsm_router
dp.include_router(common_fsm_router)
```
