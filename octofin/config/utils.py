# config/utils.py
from django.core.cache import cache
from .models import GlobalConfig
import os

def get_config(key, default=None):
    # Check cache first
    if cached := cache.get(f'config_{key}'):
        return cached

    try:
        config = GlobalConfig.objects.get(key=key)
        # Handle different config types
        if config.config_type == 'int':
            value = int(config.value)
        elif config.config_type == 'bool':
            value = config.value.lower() in ['true', '1', 'yes']
        else:
            value = config.value

        cache.set(f'config_{key}', value, timeout=60*5)  # Cache 5 minutes
        return value
    except GlobalConfig.DoesNotExist:
        # Fallback to environment variables
        env_value = os.getenv(key)
        if env_value:
            cache.set(f'config_{key}', env_value, timeout=60*5)
            return env_value
        cache.set(f'config_{key}', default, timeout=60*5)
        return default
