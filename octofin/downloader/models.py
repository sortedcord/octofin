from django.db import models

class DictionaryKey(models.Model):
    to_replace =  models.CharField(max_length=255)
    replacement = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.to_replace} -> {self.replacement}"

class DownloadTask(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('fetching', 'Fetching Metadata'),
        ('ready', 'Ready for Edit'),
        ('editing', 'Editing Metadata'),
        ('downloading', 'Downloading'),
        ('importing', 'Importing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]

    DOWNLOAD_ITEM_CHOICES = [
        ('track', 'Track'),
        ('album', 'Album'),
        ('playlist', 'Playlist')
    ]

    
    url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Store fetched metadata
    download_item = models.CharField(max_length=20, choices=DOWNLOAD_ITEM_CHOICES, default='track')

