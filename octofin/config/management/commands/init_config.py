from django.core.management.base import BaseCommand
from config.models import GlobalConfig

class Command(BaseCommand):
    help = 'Initializes configuration settings'

    def handle(self, *args, **kwargs):
        settings = [
            {'key': 'COOKIES_PATH', 'value': '', 'config_type': 'path', 'description': 'Path to cookies file'},
            {'key': 'PO_TOKEN', 'value': '', 'config_type': 'str', 'description': 'YouTube PO token'},
            {'key': 'OCTO_OUTPUT_DIR', 'value': '/music', 'config_type': 'path', 'description': 'Output directory'},
            {'key': 'LIKED_SONGS_PLAYLIST_ICON', 'value': '', 'config_type': 'path', 'description': 'Playlist icon path'},
        ]

        for setting in settings:
            GlobalConfig.objects.get_or_create(
                key=setting['key'],
                defaults={
                    'value': setting['value'],
                    'config_type': setting['config_type'],
                    'description': setting['description']
                }
            )
        self.stdout.write("Configuration initialized")
