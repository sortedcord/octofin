# likedplaylist/management/commands/sync_playlists.py
import sys
from django.core.management.base import BaseCommand
from likedplaylist.models import JellyfinAccount, AppConfig
from likedplaylist.jellyfin import sync_playlist_for_account

class Command(BaseCommand):
    help = 'Syncs liked playlists for all Jellyfin accounts'

    def handle(self, *args, **kwargs):
        config = AppConfig.get_config()
        accounts = JellyfinAccount.objects.all()
        
        for account in accounts:
            # Force flush after each print
            self.stdout.write(f"Processing account: {account.username}", ending='\n')
            self.stdout.flush()
            
            # Add more progress updates
            self.stdout.write(f"Authenticating {account.username}...")
            self.stdout.flush()
            
            sync_playlist_for_account(account, config)
            
            # Add completion message
            self.stdout.write(f"Completed sync for {account.username}", ending='\n')
            self.stdout.flush()
