from django.contrib import admin
from .models import JellyfinAccount, AppConfig

@admin.register(JellyfinAccount)
class JellyfinAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'server')

@admin.register(AppConfig)
class AppConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
