from django.db import models
from django_cryptography.fields import encrypt

class JellyfinAccount(models.Model):
    server = models.URLField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    token = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    liked_playlist_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

class AppConfig(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()

    @classmethod
    def get_config(cls):
        return {c.key: c.value for c in cls.objects.all()}
