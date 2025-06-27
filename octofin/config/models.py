from django.db import models

# config/models.py
from django.core.cache import cache

class GlobalConfigManager(models.Manager):
    def get_value(self, key, default=None):
        if (cached := cache.get(f'config_{key}')) is not None:
            return cached

        try:
            value = self.get(key=key).value
            cache.set(f'config_{key}', value, 300)  # Cache 5 minutes
            return value
        except self.model.DoesNotExist:
            return default


class GlobalConfig(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    config_type = models.CharField(max_length=10)

    objects = GlobalConfigManager()  # Assign custom manager

    def __str__(self):
        return self.key
