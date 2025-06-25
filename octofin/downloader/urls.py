from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('task/create/', views.create_task, name='create_task'),
    path('edit/<int:task_id>/', views.edit, name='edit'),
    # path('download/', views.download, name='download'),
    path('settings/', views.settings, name='settings'),
    path('queue-status/', views.queue_status, name='queue_status'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/clear/', views.clear_tasks, name='clear_tasks'),
    path('romanize/', views.romanize, name='romanize'),
]