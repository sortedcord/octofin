# config/utils.py
from django.core.cache import cache
from .models import GlobalConfig

def get_config(key, default=None):
    # Check cache first
    if cached := cache.get(f'config_{key}'):
        return cached

    try:
        value = GlobalConfig.objects.get(key=key).value
        cache.set(f'config_{key}', value, timeout=60*60)  # Cache 1 hour
        return value
    except GlobalConfig.DoesNotExist:
        cache.set(f'config_{key}', default, timeout=60*60)
        return default
