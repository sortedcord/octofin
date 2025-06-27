from django.urls import path
from .views import jellyfin_webhook, configView

urlpatterns = [
    path('webhook/', jellyfin_webhook, name='jellyfin-webhook'),
    path('', configView, name='likedplaylist-config')
]
