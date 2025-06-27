# config/admin.py
from django.contrib import admin
from .models import GlobalConfig

@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'config_type', 'description')
    search_fields = ('key',)
    list_filter = ('config_type',)
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'config_type', 'description')
        }),
    )
