import json
import os
from django.db import models
from django.conf import settings
from django.core.cache import cache

class GlobalConfigManager(models.Manager):
    def get_value(self, key, default=None):
        if (cached := cache.get(f'config_{key}')) is not None:
            return cached

        try:
            value = self.get(key=key).value
            cache.set(f'config_{key}', value, 300)
            return value
        except self.model.DoesNotExist:
            # Fallback to JSON defaults
            return self.get_json_default(key, default)

    def get_json_default(self, key, default=None):
        json_path = os.path.join(settings.BASE_DIR, 'config', 'default_settings.json')
        try:
            with open(json_path, 'r') as f:
                defaults = json.load(f)
                return defaults.get(key, {}).get('value', default)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

class GlobalConfig(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    config_type = models.CharField(max_length=10)
    group = models.CharField(max_length=255, blank=True, null=True)

    objects = GlobalConfigManager()

    def __str__(self):
        return self.key
