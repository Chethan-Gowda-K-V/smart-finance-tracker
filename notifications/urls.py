from django.urls import path
from . import views

urlpatterns = [
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:pk>/read/', views.mark_as_read, name='mark_notification_read'),
    path('api/notifications/read-all/', views.mark_all_read, name='mark_all_notifications_read'),
]
