from django.db import models

class Song(models.Model):
    # Basic identifiers
    youtube_id = models.CharField(max_length=32, unique=True)
    file = models.FileField(upload_to='songs/')
    download_date = models.DateTimeField(auto_now_add=True)

    # Core metadata
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, null=True)
    album = models.CharField(max_length=255, blank=True, null=True)
    track_number = models.PositiveIntegerField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=128, blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in seconds", blank=True, null=True)

    # Technical metadata
    bitrate = models.PositiveIntegerField(help_text="Bitrate in kbps", blank=True, null=True)
    sample_rate = models.PositiveIntegerField(help_text="Sample rate in Hz", blank=True, null=True)
    channels = models.PositiveIntegerField(help_text="Number of audio channels", blank=True, null=True)
    format = models.CharField(max_length=16, blank=True, null=True)

    # Artwork
    cover_art = models.ImageField(upload_to='cover_art/', blank=True, null=True)

    # Additional metadata
    lyrics = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # Source info
    source_url = models.URLField(blank=True, null=True)
    uploader = models.CharField(max_length=255, blank=True, null=True)
    

    def __str__(self):
        return f"{self.artist or 'Unknown Artist'} - {self.title}"


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
    
    url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Store fetched metadata
