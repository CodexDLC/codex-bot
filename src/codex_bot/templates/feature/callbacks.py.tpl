from aiogram.filters.callback_data import CallbackData

# If this is a PAIRED feature (handling buttons from Redis notifications):
# 1. Import the base callback:
# from features.redis.{feature_key}.resources.callbacks import {class_name}Callback as BaseCallback
# 2. Inherit WITHOUT a new prefix (to catch the same events):
# class {class_name}Callback(BaseCallback):
#     pass

# If this is a STANDALONE feature:
class {class_name}Callback(CallbackData, prefix="{feature_key}"):
    """Callback for the {class_name} feature."""
    action: str
    id: str | int
