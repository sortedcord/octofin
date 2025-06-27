import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from config.models import GlobalConfig

class Command(BaseCommand):
    help = 'Initializes configuration settings'

    def handle(self, *args, **kwargs):
        json_path = os.path.join(settings.BASE_DIR, 'config', 'default_settings.json')

        try:
            with open(json_path, 'r') as f:
                default_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.stdout.write(self.style.ERROR('default_settings.json not found or invalid'))
            return

        for key, config in default_settings.items():
            GlobalConfig.objects.get_or_create(
                key=key,
                defaults={
                    'value': config['value'],
                    'config_type': config['config_type'],
                    'description': config['description'],
                    'group': config['group']
                }
            )
        self.stdout.write(self.style.SUCCESS('Configuration initialized from JSON defaults'))
