from aiogram.fsm.state import State, StatesGroup

# 1. State Definition
class {class_name}States(StatesGroup):
    main = State()

STATES = {class_name}States

# 2. Garbage Collector Settings
GARBAGE_COLLECT = True

# 3. Menu Settings
MENU_CONFIG = {{
    "key": "{feature_key}",
    "text": "{class_name}",
    "description": "Description of the {class_name} feature",
    "target_state": "{feature_key}",
    "priority": 50,
    "is_admin": False,
    "is_superuser": False,
}}

# 4. Factory (DI)
def create_orchestrator(container):
    from .logic.orchestrator import {class_name}Orchestrator
    return {class_name}Orchestrator()
