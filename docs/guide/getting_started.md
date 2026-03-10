# Getting Started

## Installation

```bash
pip install codex-bot[all]
```

## Creating a Feature

```python
from codex_bot.base import BaseBotOrchestrator, ViewResultDTO, UnifiedViewDTO

class MyOrchestrator(BaseBotOrchestrator):
    def __init__(self):
        super().__init__(expected_state="MyFeature:main")

    async def render_content(self, payload) -> ViewResultDTO:
        return ViewResultDTO(text="Hello from MyFeature!")
```
